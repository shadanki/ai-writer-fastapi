from typing import Any
from openai import OpenAI
from ..config import settings
import json

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
            # temperatureパラメータを削除：GPT-5モデルの制限に従いデフォルト値を使用
        )
        text = resp.choices[0].message.content
        
        # LLMからの出力をJSONとしてパース
        try:
            parsed = json.loads(text)
            return parsed
        except json.JSONDecodeError as e:
            # エラーの詳細情報を含めて例外を発生
            error_msg = f"LLM output is not valid JSON: {text}\nJSON Error: {e}"
            if hasattr(e, 'lineno') and hasattr(e, 'colno'):
                error_msg += f"\nError at line {e.lineno}, column {e.colno}"
            raise ValueError(error_msg)

    def complete_markdown(self, system: str, user: str, temperature: float = None) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            # temperatureパラメータを削除：GPT-5モデルの制限に従いデフォルト値を使用
        )
        return resp.choices[0].message.content