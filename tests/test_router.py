"""Router tests. is_small_talk needs no network at all. The confidence-
tier and entity-anchor-override tests monkeypatch rag._semantic_search
with fixed scores instead of calling Gemini, so the calibrated decision
logic (thresholds, anchor overriding a noisier semantic hit) has a fast,
deterministic regression guard that doesn't depend on live API access or
embedding-score drift between Gemini model versions.
"""

import pytest
from rank_bm25 import BM25Okapi

from app.ai import rag
from app.ai.normalize import tokenize
from app.ai.router import Route, is_small_talk, route_message


@pytest.mark.parametrize("message,expected", [
    ("السلام عليكم", True),
    ("وعليكم السلام", True),
    ("صباح الخير", True),
    ("مساء الخير", True),
    ("شكرا جزيلا", True),
    ("مع السلامة", True),
    ("صباح الخير، بكام Gaming X؟", False),
    ("احكيلي نكتة", False),
    ("بكام Gaming X1؟", False),
])
def test_is_small_talk(message, expected):
    assert is_small_talk(message) == expected


def _fake_semantic_search(scores: dict[int, float]):

    def fake(question, chunk_embeddings, candidate_k):
        return sorted(scores.items(), key=lambda item: -item[1])[:candidate_k]

    return fake


def test_search_company_confidence_tiers(monkeypatch):

    chunks = ["chunk A - confident", "chunk B - supportive", "chunk C - below floor"]
    bm25_index = BM25Okapi([tokenize(c) for c in chunks])

    monkeypatch.setattr(
        rag, "_semantic_search",
        _fake_semantic_search({0: 0.80, 1: 0.72, 2: 0.40}),
    )

    result = rag.search_company(
        question="test question",
        chunks=chunks,
        chunk_embeddings=[None, None, None],
        bm25_index=bm25_index,
        entity_anchors=[],
    )

    assert result.confidence == "confident"
    assert result.chunks[0] == chunks[0]


def test_search_company_no_signal_is_none(monkeypatch):

    chunks = ["unrelated chunk one", "unrelated chunk two"]
    bm25_index = BM25Okapi([tokenize(c) for c in chunks])

    monkeypatch.setattr(
        rag, "_semantic_search",
        _fake_semantic_search({0: 0.60, 1: 0.55}),
    )

    result = rag.search_company(
        question="test question",
        chunks=chunks,
        chunk_embeddings=[None, None],
        bm25_index=bm25_index,
        entity_anchors=[],
    )

    assert result.confidence == "none"
    assert result.chunks == []


def test_entity_anchor_overrides_a_noisier_unrelated_semantic_hit(monkeypatch):
    """Regression test for the original motivating bug: a branch named in
    the question must lead the context even when an unrelated chunk
    scores higher by embedding noise."""

    chunks = ["فرع طنطا (الغربية):", "منتج غير متعلق عالي الدرجة"]
    bm25_index = BM25Okapi([tokenize(c) for c in chunks])

    # index 1 (the unrelated product) scores HIGHER than the real branch
    # chunk (index 0) - this is exactly the noisy-embedding scenario the
    # anchor mechanism exists to defend against.
    monkeypatch.setattr(
        rag, "_semantic_search",
        _fake_semantic_search({0: 0.40, 1: 0.71}),
    )

    anchors = [{
        "type": "branch",
        "label": "فرع طنطا",
        "chunk_index": 0,
        "aliases": {"طنطا"},
    }]

    result = rag.search_company(
        question="انتو فاتحين في طنطا؟",
        chunks=chunks,
        chunk_embeddings=[None, None],
        bm25_index=bm25_index,
        entity_anchors=anchors,
    )

    assert result.confidence == "confident"
    assert result.anchored is True
    assert result.chunks[0] == chunks[0]


def test_route_message_out_of_scope_when_domain_vocabulary_also_silent(monkeypatch):

    monkeypatch.setattr(rag, "_semantic_search", _fake_semantic_search({}))

    decision = route_message("سؤال عام لا علاقة له بالشركة إطلاقًا")

    assert decision.route == Route.OUT_OF_SCOPE
