"""Regression tests for the unsupported-category detection added after a
real bug: "موبايل في حدود 7000" surfaced an unrelated tablet (and
elsewhere, a laptop) purely because it scored well by embedding
coincidence, and "طيب عندكو ايفون؟" / "محتاج كاميرا" fell through to
generic replies instead of clearly saying the category isn't carried.

find_unsupported_category runs before any retrieval (see
app.ai.router.route_message), so every test here is fully offline - no
Gemini/Groq call is made, and several tests assert that directly by
making the mocked client raise if it's ever invoked.
"""

import pytest

from app.ai import entities, gemini_client, rag
from app.ai.router import Route, route_message


def _fail_if_called(*args, **kwargs):
    raise AssertionError("this must not be called on this code path")


# ==========================================
# Required regression cases
# ==========================================

def test_iphone_question_is_unsupported_category_not_generic_rejection(monkeypatch):
    monkeypatch.setattr(rag, "_semantic_search", _fail_if_called)

    decision = route_message("طيب عندكو ايفون؟")

    assert decision.route == Route.UNSUPPORTED_CATEGORY
    assert decision.context == "الهواتف المحمولة"


def test_camera_question_is_unsupported_category_not_out_of_scope(monkeypatch):
    monkeypatch.setattr(rag, "_semantic_search", _fail_if_called)

    decision = route_message("محتاج كاميرا")

    assert decision.route == Route.UNSUPPORTED_CATEGORY
    assert decision.context == "كاميرات التصوير"


def test_budget_mobile_question_does_not_surface_an_unrelated_product(monkeypatch):
    # Regression test for the originally reported bug: this used to reach
    # retrieval and come back with an unrelated tablet/laptop chunk.
    monkeypatch.setattr(rag, "_semantic_search", _fail_if_called)

    decision = route_message("موبايل في حدود 7000")

    assert decision.route == Route.UNSUPPORTED_CATEGORY
    assert decision.context == "الهواتف المحمولة"
    assert decision.context is not None and "تابلت" not in decision.context


def test_supported_laptop_query_is_unaffected(monkeypatch):
    # Must still go through the normal supported flow, unmodified.
    monkeypatch.setattr(rag, "_semantic_search", lambda q, e, k: [(0, 0.90)])

    match = entities.find_unsupported_category(
        "عايز لابتوب", rag.company_unsupported_category_anchors
    )
    assert match is None

    decision = route_message("عايز لابتوب")
    assert decision.route != Route.UNSUPPORTED_CATEGORY


def test_ambiguous_gaming_x_query_is_unaffected(monkeypatch):
    # Must still be free to resolve as an ambiguous *supported* query
    # (ties to specific Gaming X1/X2/X3 Pro products), never hijacked by
    # the unsupported-category check.
    match = entities.find_unsupported_category(
        "بكام Gaming X؟", rag.company_unsupported_category_anchors
    )
    assert match is None

    monkeypatch.setattr(rag, "_semantic_search", lambda q, e, k: [(0, 0.72)])

    decision = route_message("بكام Gaming X؟")
    assert decision.route != Route.UNSUPPORTED_CATEGORY


# ==========================================
# Additional coverage: variants, and the exclude_if_present safety valve
# ==========================================

@pytest.mark.parametrize("message,expected_id", [
    ("طيب عندكو ايفون؟", "MOBILE"),
    ("عايز آيفون جديد", "MOBILE"),  # alef-variant spelling, normalized the same
    ("محتاج موبايل", "MOBILE"),
    ("عندي جوال هالك", "MOBILE"),
    ("do you sell iphone?", "MOBILE"),
    ("محتاج كاميرا", "CAMERA"),
    ("عايز كاميرا رقمية كانون", "CAMERA"),
    ("camera for photography please", "CAMERA"),
])
def test_find_unsupported_category_matches_variants(message, expected_id):
    match = entities.find_unsupported_category(
        message, rag.company_unsupported_category_anchors
    )
    assert match is not None
    assert match["id"] == expected_id


@pytest.mark.parametrize("message", [
    "عايز كاميرا ويب",
    "عندكم NovaCam webcam?",
    "إيه رقم تليفون فرع طنطا؟",
    "احكيلي نكتة",
    "السلام عليكم",
])
def test_find_unsupported_category_excludes_disambiguated_or_unrelated_text(message):
    match = entities.find_unsupported_category(
        message, rag.company_unsupported_category_anchors
    )
    assert match is None


def test_webcam_query_still_reaches_normal_retrieval(monkeypatch):
    """Regression test for the exclude_if_present mechanism specifically
    at the router level: a webcam request (something we DO sell) must
    never be swallowed by the unsupported CAMERA anchor."""

    monkeypatch.setattr(rag, "_semantic_search", lambda q, e, k: [(0, 0.80)])

    decision = route_message("عايز كاميرا ويب")

    assert decision.route != Route.UNSUPPORTED_CATEGORY


def test_branch_phone_number_query_is_not_confused_with_mobile_phones(monkeypatch):
    """Regression test: "تليفون" alone would otherwise collide with a
    customer asking for a BRANCH's contact number, a legitimate supported
    query - the exclude_if_present list ("فرع", "رقم", ...) prevents it."""

    monkeypatch.setattr(rag, "_semantic_search", lambda q, e, k: [(0, 0.85)])

    decision = route_message("إيه رقم تليفون فرع طنطا؟")

    assert decision.route != Route.UNSUPPORTED_CATEGORY


# ==========================================
# Generation layer: no RAG, no Groq call for this route
# ==========================================

def test_generate_ai_reply_unsupported_category_never_calls_groq(monkeypatch):

    monkeypatch.setattr(gemini_client.groq_client.chat.completions, "create", _fail_if_called)
    monkeypatch.setattr(rag, "_semantic_search", _fail_if_called)

    reply = gemini_client.generate_ai_reply("محتاج كاميرا", [])

    assert "كاميرات التصوير" in reply
    assert "لا نوفر" in reply


def test_generate_ai_reply_unsupported_category_reply_is_concise():
    reply = gemini_client._UNSUPPORTED_CATEGORY_REPLY_TEMPLATE.format(label="الهواتف المحمولة")
    assert len(reply) < 100
    assert "الهواتف المحمولة" in reply
