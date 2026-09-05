import numpy as np
from rank_bm25 import BM25Okapi

from app.ai.normalize import tokenize
from app.ai.knowledge_base import load_all_chunks
from app.ai.embeddings import create_embeddings, cosine_similarity
from app.ai import rag_index


# ==========================================
# Semantic (embedding) search
# ==========================================

def _semantic_search(
    question: str,
    chunk_embeddings: list[np.ndarray],
    candidate_k: int
) -> list[tuple[int, float]]:

    question_embedding = create_embeddings(
        [question],
        "RETRIEVAL_QUERY"
    )[0]

    scored = [
        (index, cosine_similarity(question_embedding, embedding))
        for index, embedding in enumerate(chunk_embeddings)
    ]

    scored.sort(key=lambda item: item[1], reverse=True)

    return scored[:candidate_k]


# ==========================================
# Keyword (BM25) search
# ==========================================

def _build_bm25_index(chunks: list[str]) -> BM25Okapi:

    tokenized_chunks = [
        tokenize(chunk)
        for chunk in chunks
    ]

    return BM25Okapi(tokenized_chunks)


_KEYWORD_RELATIVE_FLOOR = 0.4


def _keyword_search(
    question: str,
    bm25_index: BM25Okapi,
    candidate_k: int
) -> list[tuple[int, float]]:

    query_tokens = tokenize(question)

    if not query_tokens:
        return []

    scores = bm25_index.get_scores(query_tokens)

    scored = [
        (index, float(score))
        for index, score in enumerate(scores)
        if score > 0
    ]

    scored.sort(key=lambda item: item[1], reverse=True)

    if not scored:
        return []

    # Keep only matches that are reasonably strong relative to the best
    # match for this question, so a single shared common word (e.g. "سعر")
    # doesn't drag in unrelated chunks alongside a clearly stronger hit.
    top_score = scored[0][1]

    scored = [
        (index, score)
        for index, score in scored
        if score >= _KEYWORD_RELATIVE_FLOOR * top_score
    ]

    return scored[:candidate_k]


# ==========================================
# Hybrid fusion (semantic + keyword, normalized weighted score fusion)
# ==========================================

_CANDIDATE_K = 15
_SEMANTIC_WEIGHT = 0.55
_KEYWORD_WEIGHT = 0.45


def _normalize_scores(scores: dict[int, float]) -> dict[int, float]:
    """Scale a {index: score} map to [0, 1] by its own max, so semantic
    (0-1 cosine) and BM25 (unbounded) scores become comparable."""

    if not scores:
        return {}

    max_score = max(scores.values())

    if max_score <= 0:
        return {index: 0.0 for index in scores}

    return {index: value / max_score for index, value in scores.items()}


def search_company(
    question: str,
    chunks: list[str],
    chunk_embeddings: list[np.ndarray],
    bm25_index: BM25Okapi,
    top_k: int = 3,
    threshold: float = 0.75
) -> list[dict]:

    semantic_hits = _semantic_search(
        question,
        chunk_embeddings,
        _CANDIDATE_K
    )

    keyword_hits = _keyword_search(
        question,
        bm25_index,
        _CANDIDATE_K
    )

    semantic_scores = dict(semantic_hits)
    keyword_scores = dict(keyword_hits)

    normalized_semantic = _normalize_scores(semantic_scores)
    normalized_keyword = _normalize_scores(keyword_scores)

    fused = []

    for index in set(semantic_scores) | set(keyword_scores):

        semantic_score = semantic_scores.get(index, 0.0)
        has_keyword_match = index in keyword_scores

        # A chunk qualifies if the embedding alone clears the original
        # similarity bar, OR it shares an actual keyword/product term with
        # the question - this catches short product-name queries (e.g.
        # "بكام ال gaming x؟") that embeddings alone can miss.
        if semantic_score < threshold and not has_keyword_match:
            continue

        # Weighted sum of each signal normalized against its own best
        # candidate, so a decisive semantic score gap isn't erased by a
        # marginal keyword-rank difference (rank-only fusion like RRF loses
        # that magnitude information, which matters once many products
        # share a common word, e.g. several "Gaming"-branded accessories).
        combined_score = (
            _SEMANTIC_WEIGHT * normalized_semantic.get(index, 0.0)
            + _KEYWORD_WEIGHT * normalized_keyword.get(index, 0.0)
        )

        fused.append(
            {
                "chunk": chunks[index],
                "score": combined_score,
                "semantic_score": semantic_score,
                "keyword_score": keyword_scores.get(index, 0.0)
            }
        )

    fused.sort(key=lambda item: item["score"], reverse=True)

    return fused[:top_k]


# ==========================================
# Company knowledge base (chunks + indexes)
# ==========================================
#
# company_embeddings is loaded from the prebuilt index on disk (see
# scripts/build_rag_index.py) instead of being computed here. The running
# app never calls Gemini to embed the knowledge base - only a missing/stale
# index does, and that fails fast at import time with a clear message
# telling the operator to run the build script, rather than crashing on a
# customer's first message.

company_chunks = load_all_chunks()
company_bm25_index = _build_bm25_index(company_chunks)
company_embeddings = rag_index.load_index(company_chunks)
