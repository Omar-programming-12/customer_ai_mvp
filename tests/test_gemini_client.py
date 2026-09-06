"""Tests for the tool-calling orchestration in app.ai.gemini_client.

test_tool_rounds_exhausted_forces_plain_text_without_400 reproduces a
real bug found in production: a warranty-policy question led the model to
call search_knowledge_base twice (once per allowed round), and the final
"force an answer" call - which used to omit `tools` entirely - let the
model attempt a third tool call anyway, which Groq rejected with 400
"Tool choice is none, but model called a tool". The fix is to pass
tool_choice="none" (with `tools` still attached) on that final call, which
this test asserts directly.
"""

import json
from unittest.mock import MagicMock

from app.ai import gemini_client, tools


def _fake_tool_call(call_id: str, name: str, arguments: dict) -> MagicMock:

    tool_call = MagicMock()
    tool_call.id = call_id
    tool_call.function.name = name
    tool_call.function.arguments = json.dumps(arguments, ensure_ascii=False)

    return tool_call


def _fake_response(content, tool_calls=None) -> MagicMock:

    message = MagicMock(content=content, tool_calls=tool_calls)

    return MagicMock(choices=[MagicMock(message=message)])


def test_tool_rounds_exhausted_forces_plain_text_without_400(monkeypatch):

    calls = []

    def fake_create(model, messages, tools=None, tool_choice=None):

        calls.append({"messages": list(messages), "tools": tools, "tool_choice": tool_choice})

        # Every round up to and including _MAX_TOOL_ROUNDS: the model keeps
        # asking for another tool call (this is exactly what was observed:
        # search_knowledge_base called twice in a row for a warranty
        # question whose context wasn't clear-cut).
        if len(calls) <= gemini_client._MAX_TOOL_ROUNDS:
            tool_call = _fake_tool_call(
                f"call-{len(calls)}", "search_knowledge_base", {"query": "مدة الضمان"}
            )
            return _fake_response(content=None, tool_calls=[tool_call])

        # The final call: the fix must have passed tool_choice="none",
        # which is what actually constrains a real Groq model to
        # plain text here instead of attempting a 3rd tool call.
        return _fake_response(content="مدة الضمان 12 شهرًا ضد عيوب التصنيع.")

    monkeypatch.setattr(gemini_client.groq_client.chat.completions, "create", fake_create)
    monkeypatch.setattr(
        tools, "TOOL_FUNCTIONS",
        {**tools.TOOL_FUNCTIONS, "search_knowledge_base": lambda query: {
            "confidence": "low_confidence", "results": ["chunk about warranty"],
        }},
    )

    reply = gemini_client._generate_with_tools("هل الضمان يغطي كسر الشاشة؟", [])

    assert reply == "مدة الضمان 12 شهرًا ضد عيوب التصنيع."

    # Exactly _MAX_TOOL_ROUNDS tool-enabled rounds, then one final call -
    # no more, no fewer, and no exception/400 raised in between.
    assert len(calls) == gemini_client._MAX_TOOL_ROUNDS + 1

    final_call = calls[-1]
    assert final_call["tool_choice"] == "none"
    assert final_call["tools"] == tools.TOOL_SPECS


def test_tool_round_returning_plain_text_stops_immediately(monkeypatch):
    """Sanity check for the common path: if the model answers without
    calling a tool on the very first round, no further rounds happen."""

    calls = []

    def fake_create(model, messages, tools=None, tool_choice=None):
        calls.append(1)
        return _fake_response(content="السلام عليكم ورحمة الله.")

    monkeypatch.setattr(gemini_client.groq_client.chat.completions, "create", fake_create)

    reply = gemini_client._generate_with_tools("السلام عليكم", [])

    assert reply == "السلام عليكم ورحمة الله."
    assert len(calls) == 1


def test_generate_ai_reply_returns_none_for_meaningless_message(monkeypatch):
    """A meaningless message must short-circuit to None before touching
    Groq at all - no reply is sent for it (see
    app.services.message_processor)."""

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Groq must not be called for a meaningless message")

    monkeypatch.setattr(gemini_client.groq_client.chat.completions, "create", fail_if_called)

    for message in ["؟", "؟؟", "..."]:
        assert gemini_client.generate_ai_reply(message, []) is None
