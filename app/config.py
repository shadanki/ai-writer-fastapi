from pydantic import BaseModel
import os
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

class Settings(BaseModel):
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./aiwriter.db")

    export_dir: str = os.getenv("EXPORT_DIR", "./exports")

    cors_origins: list[str] = (
        [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    )

settings = Settings()