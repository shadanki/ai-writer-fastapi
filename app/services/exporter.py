from pathlib import Path
from ..config import settings


def save_markdown_locally(filename: str, content: str) -> str:
    export_dir = Path(settings.export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    p = export_dir / filename
    p.write_text(content, encoding="utf-8")
    return str(p)