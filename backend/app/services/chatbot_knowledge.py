from functools import lru_cache
from pathlib import Path


@lru_cache
def load_forensics_knowledge() -> str:
    root = Path(__file__).resolve().parents[2]
    knowledge_path = root / "data" / "chatbot_knowledge" / "forensics_vi.md"
    if not knowledge_path.exists():
        return ""
    return knowledge_path.read_text(encoding="utf-8").strip()
