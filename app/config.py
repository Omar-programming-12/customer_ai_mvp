import os
from pathlib import Path


VERIFY_TOKEN = "novatech_webhook_2026"
PAGE_ID = "1338739439321269"

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


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


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
RAG_INDEX_DIR = PROJECT_ROOT / "rag_index"
