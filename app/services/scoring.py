import re
from typing import Literal

Intent = Literal["Informational", "Transactional", "Comparative"]

INFO_PAT = re.compile(r"(とは|意味|基礎|入門|使い方|解説)")
TRAN_PAT = re.compile(r"(導入|料金|費用|ツール|テンプレート|手順|やり方)")
COMP_PAT = re.compile(r"(比較|おすすめ|ランキング|ベスト|選び方)")


def infer_intents(topic: str, draft: str | None) -> list[Intent]:
    text = f"{topic} {draft or ''}"
    intents: set[Intent] = set()
    if INFO_PAT.search(text):
        intents.add("Informational")
    if TRAN_PAT.search(text):
        intents.add("Transactional")
    if COMP_PAT.search(text):
        intents.add("Comparative")
    return list(intents) or ["Informational"]


def score_title(title: str, intent: Intent | None) -> float:
    score = 0.0
    # 具体性: 数字や対象語
    if re.search(r"\d+|チェックリスト|事例|成功|失敗|完全|徹底|図解|要点", title):
        score += 0.3
    # 長さ最適
    if 32 <= len(title) <= 58:
        score += 0.3
    # 意図一致（簡易）
    if intent == "Comparative" and COMP_PAT.search(title):
        score += 0.2
    if intent == "Transactional" and TRAN_PAT.search(title):
        score += 0.2
    if intent == "Informational" and INFO_PAT.search(title):
        score += 0.2
    return round(min(score, 1.0), 3)