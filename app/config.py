import os
from pathlib import Path


VERIFY_TOKEN = "novatech_webhook_2026"
PAGE_ID = "1338739439321269"

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Meta App Secret - used only to verify the X-Hub-Signature-256 header on
# incoming webhook POSTs (HMAC-SHA256 of the raw body). Not the same
# secret as PAGE_ACCESS_TOKEN. Found in the Meta App Dashboard under
# Settings > Basic.
APP_SECRET = os.getenv("APP_SECRET")


if not PAGE_ACCESS_TOKEN:
    raise RuntimeError(
        "PAGE_ACCESS_TOKEN environment variable is missing."
    )


if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is missing."
    )


if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY environment variable is missing."
    )


if not APP_SECRET:
    raise RuntimeError(
        "APP_SECRET environment variable is missing."
    )


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
RAG_INDEX_DIR = PROJECT_ROOT / "rag_index"

# Local SQLite file for runtime state (message dedup, per-sender
# conversation history). Not part of the knowledge base and never
# committed - see .gitignore. Overridable via DB_PATH so tests (see
# tests/conftest.py) never touch the real data/app.db.
DB_PATH = Path(os.getenv("DB_PATH", str(PROJECT_ROOT / "data" / "app.db")))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
