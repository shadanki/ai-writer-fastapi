from typing import Any
from openai import OpenAI
from ..config import settings

class LLMClient:
    def __init__(self):
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def complete_json(self, system: str, user: str) -> Any:
        """JSONを返す想定のプロンプト。モデル側の出力がJSON文字列である前提。"""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.7,
        )
        text = resp.choices[0].message.content
        return text

    def complete_markdown(self, system: str, user: str, temperature: float = 0.6) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content