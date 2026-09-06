import logging
import time

from google import genai
from google.genai import types
from google.genai import errors
import numpy as np

from app.config import GEMINI_API_KEY


logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "gemini-embedding-001"

_embedding_client = genai.Client(
    api_key=GEMINI_API_KEY
)

# Gemini's embed_content rejects a single request with more than 100 items.
_BATCH_SIZE = 100

# The Free Tier also rate-limits embedding throughput (observed ~100 inputs
# per minute), independent of the per-request item cap above. Retrying with
# backoff on 429 reacts to whatever the real limit is instead of guessing a
# fixed sleep, so it keeps working even if the quota changes later.
_MAX_RETRIES = 5
_INITIAL_BACKOFF_SECONDS = 20
_MAX_BACKOFF_SECONDS = 90


def _embed_batch_with_retry(batch: list[str], task_type: str):

    delay = _INITIAL_BACKOFF_SECONDS

    for attempt in range(1, _MAX_RETRIES + 1):

        try:
            return _embedding_client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type=task_type
                )
            )

        except errors.ClientError as error:

            is_rate_limited = error.code == 429

            if not is_rate_limited or attempt == _MAX_RETRIES:
                raise

            logger.warning(
                "Gemini rate limit hit (attempt %d/%d), waiting %ds before retrying...",
                attempt, _MAX_RETRIES, delay,
            )

            time.sleep(delay)
            delay = min(delay * 2, _MAX_BACKOFF_SECONDS)


def create_embeddings(
    texts: list[str],
    task_type: str
) -> list[np.ndarray]:

    embeddings: list[np.ndarray] = []

    for start in range(0, len(texts), _BATCH_SIZE):

        batch = texts[start:start + _BATCH_SIZE]
        response = _embed_batch_with_retry(batch, task_type)

        embeddings.extend(
            np.array(embedding.values, dtype=np.float32)
            for embedding in response.embeddings
        )

    return embeddings


def cosine_similarity(
    a: np.ndarray,
    b: np.ndarray
) -> float:

    denominator = (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(a, b) / denominator
    )


def prepare_company_embeddings(
    chunks: list[str]
) -> list[np.ndarray]:

    return create_embeddings(
        chunks,
        "RETRIEVAL_DOCUMENT"
    )
