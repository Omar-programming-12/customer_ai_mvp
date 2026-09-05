from dataclasses import dataclass

import numpy as np
from rank_bm25 import BM25Okapi

from app.ai.normalize import tokenize
from app.ai.knowledge_base import load_all_chunks
from app.ai.embeddings import create_embeddings, cosine_similarity
from app.ai import rag_index
from app.ai import entities


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

# Keyword score is a tie-breaker among qualified chunks, not a co-equal
# ranking signal. Measured on the real BM25 index: raw scores are inflated
# by document length (a short "mouse" chunk sharing one word like "gaming"
# can out-score a longer, genuinely-matching laptop chunk purely because
# BM25 normalizes by document length), so a keyword-vs-semantic blend with
# comparable weights let that length artifact outrank a real ~0.05
# semantic gap - exactly the width of the relevant/noise gap measured
# above. Keeping this weight small still lets keyword separate near-equal
# semantic candidates (e.g. which of X1/X2/X3 Pro to lead with) without
# ever letting it flip semantic ordering on its own.
_KEYWORD_TIEBREAK_WEIGHT = 0.05

# Three-tier semantic gate, from strongest to weakest evidence.
#
# Calibrated against real gemini-embedding-001 cosine scores measured on
# this knowledge base (not guessed): for short Arabic queries against these
# chunks, even a CLEARLY UNRELATED pair (e.g. "احكيلي نكتة" vs a branch
# address, or vs a generic policy header) sits at ~0.57-0.67 baseline -
# much higher than a typical embedding "noise floor". Genuinely relevant
# pairs (a named branch, a matched product, a topically-matched policy
# chunk) measured at ~0.70-0.79. So the gate has to sit inside that ~0.03
# gap around 0.68-0.70, not at a textbook-typical 0.3-0.5:
#
# 1) >= _SEMANTIC_CONFIDENT_THRESHOLD (0.75): the embedding alone is
#    trusted - only the strongest, most direct matches clear this
#    (e.g. an exact branch-name query measured at 0.785).
# 2) >= _SEMANTIC_SUPPORTIVE_THRESHOLD (0.70): sits right above the
#    measured noise ceiling (~0.667) and at the measured relevant floor -
#    kept as low-confidence evidence even with no keyword overlap.
# 3) >= _SEMANTIC_KEYWORD_ASSISTED_THRESHOLD (0.68) *and* a keyword hit: a
#    narrow grace band just below the supportive bar, only trusted when a
#    real shared term backs it up - this is what still lets short/awkward
#    product-name queries in without reopening the noise band to keyword
#    matches alone.
#
# What no longer qualifies: a keyword match with embedding relevance at or
# below the measured noise ceiling. That used to be sufficient by itself
# and is exactly how a generic shared word (e.g. "amd" appearing in a
# handful of unrelated laptop specs, or "gaming" shared by 16 different
# products) could drag an unrelated chunk into the context - and, before
# recalibration against real scores, how an out-of-scope question (e.g. a
# joke request landing at ~0.65 against a generic policy header) could
# still slip in as "low confidence" instead of being rejected.
_SEMANTIC_CONFIDENT_THRESHOLD = 0.75
_SEMANTIC_SUPPORTIVE_THRESHOLD = 0.70
_SEMANTIC_KEYWORD_ASSISTED_THRESHOLD = 0.68


def _normalize_scores(scores: dict[int, float]) -> dict[int, float]:
    """Scale a {index: score} map to [0, 1] by its own max, so semantic
    (0-1 cosine) and BM25 (unbounded) scores become comparable."""

    if not scores:
        return {}

    max_score = max(scores.values())

    if max_score <= 0:
        return {index: 0.0 for index in scores}

    return {index: value / max_score for index, value in scores.items()}


@dataclass
class RetrievalResult:
    """What routing needs to know about a retrieval attempt - not just
    which chunks were accepted, but how much to trust them."""

    chunks: list[str]
    # "confident"      -> an entity anchor fired, or a chunk cleared the
    #                     confident embedding bar on its own.
    # "low_confidence" -> some relevant signal exists, but none of it is
    #                     strong enough to trust as a definite answer.
    # "none"           -> no meaningful signal at all.
    confidence: str
    anchored: bool
    top_semantic_score: float
    top_keyword_score: float


def search_company(
    question: str,
    chunks: list[str],
    chunk_embeddings: list[np.ndarray],
    bm25_index: BM25Okapi,
    entity_anchors: list[dict] | None = None,
    top_k: int = 3
) -> RetrievalResult:

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

    qualified = []

    for index in set(semantic_scores) | set(keyword_scores):

        semantic_score = semantic_scores.get(index, 0.0)
        has_keyword_match = index in keyword_scores

        is_confident = semantic_score >= _SEMANTIC_CONFIDENT_THRESHOLD
        is_supported = (
            semantic_score >= _SEMANTIC_SUPPORTIVE_THRESHOLD
            or (
                semantic_score >= _SEMANTIC_KEYWORD_ASSISTED_THRESHOLD
                and has_keyword_match
            )
        )

        # Every accepted chunk needs at least some embedding relevance of
        # its own - a keyword match can corroborate a borderline embedding
        # score, but can no longer carry a chunk in on its own with (near)
        # zero semantic support.
        if not is_confident and not is_supported:
            continue

        # Rank by the real (un-normalized) semantic score first - it's the
        # calibrated signal - and let keyword act only as a small
        # tie-breaker on top of it. Normalizing keyword score by its own
        # per-query max and blending it in at a comparable weight would let
        # a BM25 length-normalization artifact (a short chunk sharing one
        # word scoring higher than a longer, genuinely relevant chunk)
        # outrank a real semantic gap - measured, not hypothetical, on this
        # index (see _KEYWORD_TIEBREAK_WEIGHT).
        combined_score = (
            semantic_score
            + _KEYWORD_TIEBREAK_WEIGHT * normalized_keyword.get(index, 0.0)
        )

        qualified.append(
            {
                "index": index,
                "chunk": chunks[index],
                "score": combined_score,
                "is_confident": is_confident,
            }
        )

    qualified.sort(key=lambda item: item["score"], reverse=True)

    anchor_matches = entities.find_anchor_matches(question, entity_anchors or [])
    anchored_indexes = {anchor["chunk_index"] for anchor in anchor_matches}

    # Anchored chunks are deterministic ground truth for a known entity in
    # the question, so they lead the context ahead of anything ranked only
    # by embedding/keyword score - a noisy semantic hit (e.g. an unrelated
    # GPU product) never crowds out the branch the customer actually named.
    ordered_indexes: list[int] = [index for index in anchored_indexes]

    for item in qualified:
        if item["index"] not in ordered_indexes:
            ordered_indexes.append(item["index"])

    top_indexes = ordered_indexes[:top_k]

    if anchored_indexes or any(item["is_confident"] for item in qualified):
        confidence = "confident"
    elif qualified:
        confidence = "low_confidence"
    else:
        confidence = "none"

    return RetrievalResult(
        chunks=[chunks[index] for index in top_indexes],
        confidence=confidence,
        anchored=bool(anchored_indexes),
        top_semantic_score=max(semantic_scores.values(), default=0.0),
        top_keyword_score=max(keyword_scores.values(), default=0.0),
    )


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
company_entity_anchors = entities.build_branch_anchors(company_chunks)
