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
    
    try:
        raw = llm.complete_json(SYSTEM_PROMPT, prompt)
        
        # LLMからの出力を適切にパース
        if isinstance(raw, str):
            data = json.loads(raw)
        else:
            data = raw
            
        # データが配列でない場合は配列に変換
        if not isinstance(data, list):
            if isinstance(data, dict):
                data = [data]
            else:
                data = []
                
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse titles from LLM output: {raw}")
    except Exception as e:
        raise ValueError(f"Error generating titles: {str(e)}")

    # 保存＆スコアリング
    results: list[dict[str, Any]] = []
    for item in data:
        # itemが辞書でない場合はスキップ
        if not isinstance(item, dict):
            continue
            
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
    
    try:
        raw = llm.complete_json(SYSTEM_PROMPT, prompt)
        
        # まずは raw の型で分岐（complete_json が既に dict/list を返すことがある）
        if isinstance(raw, (dict, list)):
            data = raw
        else:
            # 次に JSON 文字列としてパース
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                # JSONパースに失敗した場合はエラーを発生させる
                raise ValueError(f"Failed to parse outline from LLM output: {raw}")
        
        # データの構造を検証
        if isinstance(data, dict):
            required_keys = ["intro", "title", "h2", "outro"]
            missing_keys = [key for key in required_keys if key not in data]
            if missing_keys:
                raise ValueError(f"Missing required keys in outline: {missing_keys}")
            
            if not isinstance(data.get("h2"), list):
                raise ValueError("h2 must be a list")
        
        # 保存
        prj.article.outline = data
        db.commit()
        return data
        
    except Exception as e:
        raise


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

    # 記事タイトル（H1）
    title_text = outline_data.get("title", "")
    if title_text:
        title_md = f"# {title_text}\n\n"
        sections_md.append(title_md)

    # H2/H3ごとにセクション生成
    for h2 in outline_data.get("h2", []):
        h2_title = h2.get("title")
        if not h2_title:
            continue
        
        # H2セクションの開始（記事のメイン見出し）
        h2_md = f"## {h2_title}\n\n"
        if h2.get("keypoints"):
            h2_md += "**要点：**\n"
            for point in h2["keypoints"]:
                h2_md += f"- {point}\n"
            h2_md += "\n"
        sections_md.append(h2_md)
        
        # H3セクションの生成
        for h3 in h2.get("h3", []):
            h3_title = h3.get("title")
            if not h3_title:
                continue
            sec_prompt = SECTION_PROMPT.format(h2_title=h3_title)
            md = llm.complete_markdown(SYSTEM_PROMPT, sec_prompt)
            # 簡単な見出し調整
            if not md.strip().startswith("###"):
                md = f"### {h3_title}\n\n" + md
            sections_md.append(md + "\n\n")

    # まとめ
    outro_text = outline_data.get("outro", "")
    outro_md = f"## まとめ\n\n{outro_text}\n"
    sections_md.append(outro_md)

    # 最終整形
    joined = "\n".join(sections_md)
    final_md = llm.complete_markdown(SYSTEM_PROMPT, FINAL_POLISH_PROMPT.format(glossary="") + "\n\n" + joined)
    
    # Front Matter付与（アウトラインの導入文を description に）
    description = outline_data.get("intro", "") if isinstance(outline_data, dict) else ""
    fm = front_matter(
        prj.article.selected_title,
        description=description,
        tags=[prj.topic, "入門", "実践ガイド"],
        lang=prj.language,
    )

    # 保存
    prj.article.markdown = final_md
    db.commit()
    return (prj.article.markdown, sections_md)
