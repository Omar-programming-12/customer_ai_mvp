from unittest.mock import patch

from app.services.message_processor import process_message


async def test_process_message_success_sends_reply_and_saves_history(temp_db):

    sent = []

    async def fake_send(psid, text):
        sent.append((psid, text))

    with patch(
        "app.services.message_processor.generate_ai_reply",
        return_value="ok reply",
    ) as fake_reply, patch(
        "app.services.message_processor.send_message_to_messenger",
        side_effect=fake_send,
    ):
        await process_message("psid-x", "hello", "mid-x")

    assert sent == [("psid-x", "ok reply")]
    fake_reply.assert_called_once_with("hello", [])

    from app.ai import memory
    assert memory.get_history("psid-x") == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "ok reply"},
    ]


async def test_process_message_second_turn_receives_first_turns_history(temp_db):

    sent = []

    async def fake_send(psid, text):
        sent.append((psid, text))

    def fake_generate(text, history=None):
        return f"echo: {text} (history_len={len(history or [])})"

    with patch(
        "app.services.message_processor.generate_ai_reply",
        side_effect=fake_generate,
    ), patch(
        "app.services.message_processor.send_message_to_messenger",
        side_effect=fake_send,
    ):
        await process_message("psid-y", "بكام Gaming X1؟", "mid-1")
        await process_message("psid-y", "وكام Gaming X2؟", "mid-2")

    assert "history_len=0" in sent[0][1]
    assert "history_len=2" in sent[1][1]


async def test_process_message_failure_sends_fallback_and_skips_history(temp_db):

    sent = []

    async def fake_send(psid, text):
        sent.append((psid, text))

    with patch(
        "app.services.message_processor.generate_ai_reply",
        side_effect=RuntimeError("boom"),
    ), patch(
        "app.services.message_processor.send_message_to_messenger",
        side_effect=fake_send,
    ):
        await process_message("psid-z", "hello", "mid-z")

    assert len(sent) == 1
    assert "مشكلة مؤقتة" in sent[0][1]

    from app.ai import memory
    # A failed turn is never recorded - a half-answered exchange would
    # only confuse the next turn's history-based context.
    assert memory.get_history("psid-z") == []


async def test_process_message_meaningless_sends_nothing_and_skips_history(temp_db):
    """generate_ai_reply returning None (Route.MEANINGLESS) must result in
    no Messenger send at all and no conversation-history entry - not even
    a fixed reply, per the desired UX (silence, not a canned rejection)."""

    sent = []

    async def fake_send(psid, text):
        sent.append((psid, text))

    with patch(
        "app.services.message_processor.generate_ai_reply",
        return_value=None,
    ) as fake_reply, patch(
        "app.services.message_processor.send_message_to_messenger",
        side_effect=fake_send,
    ):
        await process_message("psid-w", "؟؟", "mid-w")

    fake_reply.assert_called_once_with("؟؟", [])
    assert sent == []

    from app.ai import memory
    assert memory.get_history("psid-w") == []
