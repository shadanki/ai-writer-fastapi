import json
from typing import Any
from sqlalchemy.orm import Session
from ..models import Project, TitleCandidate, Article
from ..prompts import SYSTEM_PROMPT, TITLE_PROMPT, OUTLINE_PROMPT, SECTION_PROMPT, FINAL_POLISH_PROMPT
from .llm import LLMClient
from .scoring import infer_intents, score_title
from ..utils.text import front_matter
import re


def _get_project(db: Session, pid: str) -> Project:
    prj = db.get(Project, pid)
    if not prj:
        raise ValueError("Invalid sessionId")
    return prj


def generate_titles(db: Session, session_id: str, max_candidates: int = 10) -> list[dict[str, Any]]:
    print(f"DEBUG: generate_titles called with session_id: {session_id}, max_candidates: {max_candidates}")
    
    try:
        prj = _get_project(db, session_id)
        print(f"DEBUG: Project found: {prj.topic}")
    except Exception as e:
        print(f"ERROR: Failed to get project: {e}")
        raise e
    
    intents = infer_intents(prj.topic, prj.draft)
    prompt = TITLE_PROMPT.format(
        intent_list="Informational|Transactional|Comparative",
        topic=prj.topic,
        draft=(prj.draft or "(なし)"),
        inferred_intents=", ".join(intents),
    )
    
    print(f"DEBUG: Generating titles for topic: {prj.topic}")
    print(f"DEBUG: Inferred intents: {intents}")
    print(f"DEBUG: Prompt: {prompt}")
    
    llm = LLMClient()
    try:
        print(f"DEBUG: Calling LLM...")
        raw = llm.complete_json(SYSTEM_PROMPT, prompt)
        print(f"DEBUG: Raw LLM output: {raw}")
        print(f"DEBUG: Raw output type: {type(raw)}")
        print(f"DEBUG: Raw output length: {len(raw) if isinstance(raw, str) else 'N/A'}")
    except Exception as e:
        print(f"ERROR: LLM call failed: {e}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        raise e
    
    # data変数を初期化
    data = []
    
    try:
        print(f"DEBUG: Attempting to parse JSON...")
        
        # ```jsonで囲まれている場合の処理
        if raw.strip().startswith("```json"):
            # ```jsonと```を除去
            cleaned_raw = raw.strip()
            if cleaned_raw.startswith("```json"):
                cleaned_raw = cleaned_raw[7:]  # "```json"を除去
            if cleaned_raw.endswith("```"):
                cleaned_raw = cleaned_raw[:-3]  # "```"を除去
            cleaned_raw = cleaned_raw.strip()
            print(f"DEBUG: Cleaned raw output: {cleaned_raw}")
            raw = cleaned_raw
        
        data = json.loads(raw)
        print(f"DEBUG: Parsed JSON data: {data}")
        print(f"DEBUG: Parsed data type: {type(data)}")
        
        # データの構造を確認
        if not isinstance(data, list):
            print(f"WARNING: Expected list but got: {type(data)}")
            raise ValueError("Expected list but got: " + str(type(data)))
        
        print(f"DEBUG: Data is a list with {len(data)} items")
        
        # 各アイテムの構造を確認
        for i, item in enumerate(data):
            print(f"DEBUG: Item {i}: {item}")
            if not isinstance(item, dict):
                print(f"WARNING: Expected dict but got: {type(item)}")
                raise ValueError("Expected dict but got: " + str(type(item)))
            if "title" not in item:
                print(f"WARNING: Missing 'title' field in item: {item}")
                raise ValueError("Missing 'title' field in item: " + str(item))
                
    except Exception as json_error:
        print(f"JSON parsing failed: {json_error}")
        print(f"Raw output: {raw}")
        
        # 出力がJSONでないときのフォールバック（箇条書き→配列化などを簡易整形）
        lines = [l.strip("- • ") for l in raw.splitlines() if l.strip()]
        print(f"DEBUG: Extracted lines: {lines}")
        
        # 空行やJSONの残りを除外（より厳密に）
        filtered_lines = []
        for line in lines:
            # ```json、```、{、[で始まる行を除外
            if line.startswith("```") or line.startswith("{") or line.startswith("["):
                continue
            # 行の中に```jsonが含まれている場合は除外
            if "```json" in line or "```" in line:
                continue
            # 空行でない場合のみ追加
            if line.strip():
                filtered_lines.append(line)
        
        print(f"DEBUG: Filtered lines: {filtered_lines}")
        
        data = [{"title": l, "intent": None, "why": None} for l in filtered_lines if l]
        print(f"Fallback data: {data}")

    print(f"DEBUG: Final data to process: {data}")
    print(f"DEBUG: Data type: {type(data)}")
    print(f"DEBUG: Data length: {len(data) if isinstance(data, list) else 'N/A'}")

    # 保存＆スコアリング
    results: list[dict[str, Any]] = []
    for i, item in enumerate(data):
        print(f"DEBUG: Processing item {i}: {item}")
        
        title = (item.get("title") or "").strip()
        if not title:
            print(f"DEBUG: Skipping item {i} - empty title")
            continue
            
        # タイトルが不正な形式の場合のクリーンアップ
        if title.startswith('{"title":'):
            # JSON文字列が混入している場合の処理
            try:
                # 部分的なJSONを抽出
                title_match = re.search(r'"title":\s*"([^"]+)"', title)
                if title_match:
                    title = title_match.group(1)
                    print(f"DEBUG: Extracted title from JSON: {title}")
                else:
                    # 完全に不正な場合はスキップ
                    print(f"DEBUG: Skipping item {i} - invalid JSON format")
                    continue
            except:
                print(f"DEBUG: Skipping item {i} - JSON extraction failed")
                continue
        
        # その他の不正な文字を除去（より厳密に）
        # ```json、```、{、[などの不正な文字を完全に除去
        title = title.replace('```json', '').replace('```', '').replace('{', '').replace('}', '').replace('[', '').replace(']', '')
        title = title.strip()
        
        # 不正な文字が残っている場合はスキップ
        if any(char in title for char in ['```', '{', '}', '[', ']', '"', '\\']):
            print(f"DEBUG: Skipping item {i} - contains invalid characters: '{title}'")
            continue
            
        if not title or len(title) < 5:  # 短すぎるタイトルは除外
            print(f"DEBUG: Skipping item {i} - title too short: '{title}'")
            continue
            
        intent = item.get("intent")
        why = item.get("why")
        
        print(f"DEBUG: Calling score_title for: {title}")
        sc = score_title(title, intent)
        print(f"DEBUG: Score result: {sc}")
        
        print(f"DEBUG: Adding candidate: title='{title}', intent='{intent}', score={sc}")
        
        try:
            cand = TitleCandidate(project_id=prj.id, title=title, intent=intent, score=sc, why=why, raw=item)
            db.add(cand)
            db.flush()  # cand.id を取得
            results.append({"id": cand.id, "title": title, "intent": intent, "score": sc, "why": why})
            print(f"DEBUG: Successfully added candidate with ID: {cand.id}")
        except Exception as db_error:
            print(f"ERROR: Failed to add candidate to database: {db_error}")
            import traceback
            print(f"ERROR: Database error traceback: {traceback.format_exc()}")

    print(f"DEBUG: Final results count: {len(results)}")
    print(f"DEBUG: Results: {results}")
    
    try:
        db.commit()
        print(f"DEBUG: Database commit successful")
    except Exception as commit_error:
        print(f"ERROR: Database commit failed: {commit_error}")
        db.rollback()
        raise commit_error
    
    # スコアで上位を返す
    results.sort(key=lambda x: x.get("score") or 0.0, reverse=True)
    final_results = results[:max_candidates]
    print(f"DEBUG: Returning {len(final_results)} results")
    return final_results


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
    except Exception as e:
        raise e
    
    try:
        data = json.loads(raw)
    except Exception:
        # ざっくりフォールバック
        data = {
            "intro": "この記事では要点をわかりやすく解説します。",
            "h1": [
                {
                    "title": "基本の理解", 
                    "h2": [
                        {"title": "定義", "h3": ["概念", "背景"]}
                    ], 
                    "keypoints": ["定義", "目的", "効果"]
                },
                {
                    "title": "実践の手順", 
                    "h2": [
                        {"title": "準備", "h3": ["環境", "ツール"]},
                        {"title": "導入", "h3": ["設定", "確認"]}
                    ], 
                    "keypoints": ["手順", "注意点", "成功のコツ"]
                },
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

    # 導入
    intro_text = outline_data.get("intro", "")
    intro_md = f"# 導入\n\n{intro_text}\n\n"
    
    # H1セクションを順次生成
    h1_sections = outline_data.get("h1", [])
    sections_md = []
    
    for h1_section in h1_sections:
        h1_title = h1_section.get("title", "")
        h1_keypoints = h1_section.get("keypoints", [])
        
        # H1セクションの開始
        section_md = f"# {h1_title}\n\n"
        
        # H2セクションを生成
        h2_sections = h1_section.get("h2", [])
        for h2_section in h2_sections:
            h2_title = h2_section.get("title", "")
            h3_items = h2_section.get("h3", [])
            
            # H2セクションの開始
            section_md += f"## {h2_title}\n\n"
            
            # H3項目を箇条書きで追加
            for h3_item in h3_items:
                section_md += f"- {h3_item}\n"
            section_md += "\n"
        
        # キーポイントを追加
        if h1_keypoints:
            section_md += "**キーポイント:**\n"
            for point in h1_keypoints:
                section_md += f"- {point}\n"
            section_md += "\n"
        
        sections_md.append(section_md)
    
    # まとめ
    outro_text = outline_data.get("outro", "")
    outro_md = f"# まとめ\n\n{outro_text}\n"
    
    # 全セクションを結合
    all_sections = [intro_md] + sections_md + [outro_md]
    joined = "\n".join(all_sections)
    
    # 最終整形
    llm = LLMClient()
    glossary = "用語統一: DX, プロジェクト管理, KGI/KPI"
    final_md = llm.complete_markdown(SYSTEM_PROMPT, FINAL_POLISH_PROMPT.format(glossary=glossary) + "\n\n" + joined)

    # タイトルは記事本文に含めない（記事タイトルとして別途表示）
    full_md = final_md or joined

    # 保存
    prj.article.markdown = full_md
    db.commit()
    return (prj.article.markdown, all_sections)