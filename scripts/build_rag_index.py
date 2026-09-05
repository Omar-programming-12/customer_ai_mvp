"""
Builds the offline RAG index (embeddings for every knowledge-base chunk)
and saves it to disk under rag_index/.

The running FastAPI app never calls Gemini to embed the knowledge base -
it only loads what this script produces (app/ai/rag.py, at import time).
Run this script once, and again any time knowledge_base/ changes.

Handles Gemini's Free Tier limits:
- max 100 items per embed_content request (batched automatically)
- an embedding-throughput rate limit (retried with backoff on HTTP 429)
(both handled by app.ai.embeddings.create_embeddings, reused here so the
batching/retry logic isn't duplicated between the app and this script)

Usage:
    python scripts/build_rag_index.py

Requires PAGE_ACCESS_TOKEN and GEMINI_API_KEY in the environment (both are
validated by app.config on import, even though only GEMINI_API_KEY is used
here - set PAGE_ACCESS_TOKEN to any placeholder value if running this
script outside the full app environment).
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ai.knowledge_base import load_all_chunks
from app.ai.embeddings import prepare_company_embeddings
from app.ai import rag_index


def main() -> None:

    chunks = load_all_chunks()

    print(f"Building embeddings for {len(chunks)} chunks...")
    print("This may take a few minutes on the Gemini Free Tier due to rate limits.")

    started_at = time.monotonic()
    embeddings = prepare_company_embeddings(chunks)
    elapsed_seconds = time.monotonic() - started_at

    rag_index.save_index(chunks, embeddings)

    print(
        f"Saved {len(embeddings)} embeddings to {rag_index.RAG_INDEX_DIR} "
        f"in {elapsed_seconds:.1f}s."
    )


if __name__ == "__main__":
    main()
