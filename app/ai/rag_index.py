import hashlib
import json
from datetime import datetime, timezone

import numpy as np

from app.config import RAG_INDEX_DIR
from app.ai.embeddings import EMBEDDING_MODEL


_EMBEDDINGS_FILE = RAG_INDEX_DIR / "embeddings.npy"
_METADATA_FILE = RAG_INDEX_DIR / "metadata.json"

_REBUILD_HINT = "Run `python scripts/build_rag_index.py` to (re)build it."


def compute_chunks_fingerprint(chunks: list[str]) -> str:
    """Order-sensitive fingerprint of the exact chunk list an index was
    built from, so a stale/mismatched index is detected instead of silently
    pairing the wrong embedding with the wrong chunk."""

    hasher = hashlib.sha256()

    for chunk in chunks:
        hasher.update(chunk.encode("utf-8"))
        hasher.update(b"\x1f")

    return hasher.hexdigest()


def save_index(chunks: list[str], embeddings: list[np.ndarray]) -> None:

    RAG_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    matrix = np.stack(embeddings).astype(np.float32)
    np.save(_EMBEDDINGS_FILE, matrix)

    metadata = {
        "model": EMBEDDING_MODEL,
        "chunk_count": len(chunks),
        "embedding_dim": int(matrix.shape[1]),
        "chunks_fingerprint": compute_chunks_fingerprint(chunks),
        "built_at": datetime.now(timezone.utc).isoformat(),
    }

    _METADATA_FILE.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def load_index(current_chunks: list[str]) -> list[np.ndarray]:

    if not _EMBEDDINGS_FILE.exists() or not _METADATA_FILE.exists():
        raise RuntimeError(
            "No prebuilt RAG index found under "
            f"{RAG_INDEX_DIR}. {_REBUILD_HINT}"
        )

    metadata = json.loads(_METADATA_FILE.read_text(encoding="utf-8"))

    if metadata.get("model") != EMBEDDING_MODEL:
        raise RuntimeError(
            f"The prebuilt RAG index was built with model "
            f"'{metadata.get('model')}', but the app expects "
            f"'{EMBEDDING_MODEL}'. {_REBUILD_HINT}"
        )

    current_fingerprint = compute_chunks_fingerprint(current_chunks)

    if metadata.get("chunks_fingerprint") != current_fingerprint:
        raise RuntimeError(
            "The prebuilt RAG index does not match the current knowledge "
            "base (knowledge_base/ has changed since the index was built). "
            f"{_REBUILD_HINT}"
        )

    matrix = np.load(_EMBEDDINGS_FILE)

    return [row for row in matrix]
