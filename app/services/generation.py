import json
from typing import Any
from sqlalchemy.orm import Session
from ..models import Project, TitleCandidate, Article
from ..prompts import SYSTEM_PROMPT, TITLE_PROMPT, OUTLINE_PROMPT, SECTION_PROMPT, FINAL_POLISH_PROMPT
from .llm import LLMClient
from .scoring import infer_intents, score_title
from ..utils.text import front_matter


def _get_project(db: Session, pid: str) -> Project:
    prj = db.get(Project, pid)
    if not prj:
        raise ValueError("Invalid sessionId")
    return prj


def generate_titles(db: Session, session_id: str, max_candidates: int = 10) -> list[dict[str, Any]]:
    prj = _get_project(db, session_id)
    intents = infer_intents(prj.topic, prj.draft)
    prompt = TITLE_PROMPT.format(
        intent_list="Informational|Transactional|Comparative",
        topic=prj.topic,
        draft=(prj.draft or "(なし)"),
        inferred_intents=", ".join(intents),
    )
    llm = LLMClient()
    raw = llm.complete_json(SYSTEM_PROMPT, prompt)
    try:
        data = json.loads(raw)
    except Exception:
        # 出力がJSONでないときのフォールバック（箇条書き→配列化などを簡易整形）
        lines = [l.strip("- • ") for l in raw.splitlines() if l.strip()]
        data = [{"title": l, "intent": None, "why": None} for l in lines if l]

    # 保存＆スコアリング
    results: list[dict[str, Any]] = []
    for item in data:
        title = (item.get("title") or "").strip()
        if not title:
            continue
        intent = item.get("intent")
        why = item.get("why")
        sc = score_title(title, intent)
        cand = TitleCandidate(project_id=prj.id, title=title, intent=intent, score=sc, why=why, raw=item)
        db.add(cand)
        db.flush()  # cand.id を取得
        results.append({"id": cand.id, "title": title, "intent": intent, "score": sc, "why": why})

    db.commit()
    # スコアで上位を返す
    results.sort(key=lambda x: x.get("score") or 0.0, reverse=True)
    return results[:max_candidates]


def select_title(db: Session, session_id: str, candidate_id: str) -> Article:
    prj = _get_project(db, session_id)
    cand = db.get(TitleCandidate, candidate_id)
    if not cand or cand.project_id != prj.id:
        raise ValueError("candidateId not found for this session")

    art = prj.article
    if not art:
        art = Article(project_id=prj.id, selected_title=cand.title)
        db.add(art)
    else:
        art.selected_title = cand.title
    db.commit()
    db.refresh(art)
    return art


def generate_outline(db: Session, session_id: str) -> dict[str, Any]:
    prj = _get_project(db, session_id)
    if not prj.article or not prj.article.selected_title:
        raise ValueError("No selected title")

    llm = LLMClient()
    prompt = OUTLINE_PROMPT.format(selected_title=prj.article.selected_title)
    raw = llm.complete_json(SYSTEM_PROMPT, prompt)
    try:
        data = json.loads(raw)
    except Exception:
        # ざっくりフォールバック
        data = {
            "intro": "この記事では要点をわかりやすく解説します。",
            "h2": [
                {"title": "基本の理解", "h3": ["定義", "背景"], "keypoints": ["定義", "目的", "効果"]},
                {"title": "実践の手順", "h3": ["準備", "導入"], "keypoints": ["手順", "注意点", "成功のコツ"]},
            ],
            "outro": "実行の第一歩を踏み出しましょう。",
        }

    # 保存
    prj.article.outline = data
    db.commit()
    return data


def generate_article(db: Session, session_id: str, outline: dict | None = None) -> tuple[str, list[str]]:
    prj = _get_project(db, session_id)
    if not prj.article or not prj.article.selected_title:
        raise ValueError("No selected title")

    outline_data = outline or prj.article.outline
    if not outline_data:
        raise ValueError("No outline available")

    llm = LLMClient()
    sections_md: list[str] = []

    # 導入
    intro_text = outline_data.get("intro", "")
    intro_md = f"## 導入\n\n{intro_text}\n\n"
    sections_md.append(intro_md)

    # H2/H3ごとにセクション生成
    for h2 in outline_data.get("h2", []):
        h2_title = h2.get("title")
        if not h2_title:
            continue
        sec_prompt = SECTION_PROMPT.format(h2_title=h2_title)
        md = llm.complete_markdown(SYSTEM_PROMPT, sec_prompt)
        # 簡単な見出し調整
        if not md.strip().startswith("##"):
            md = f"## {h2_title}\n\n" + md
        sections_md.append(md + "\n\n")

    # まとめ
    outro_text = outline_data.get("outro", "")
    outro_md = f"## まとめ\n\n{outro_text}\n"
    sections_md.append(outro_md)

    # 最終整形
    joined = "\n".join(sections_md)
    glossary = "用語統一: DX, プロジェクト管理, KGI/KPI"
    final_md = llm.complete_markdown(SYSTEM_PROMPT, FINAL_POLISH_PROMPT.format(glossary=glossary) + "\n\n" + joined)

    # Front Matter付与
    fm = front_matter(prj.article.selected_title, description=outline_data.get("intro", ""), tags=[prj.topic, "入門", "実践ガイド"], lang=prj.language)
    full_md = fm + "# " + prj.article.selected_title + "\n\n> 本記事の要点は本文冒頭の箇条書きを参照してください。\n\n" + joined

    # 保存
    prj.article.markdown = final_md or full_md
    db.commit()
    return (prj.article.markdown, sections_md)