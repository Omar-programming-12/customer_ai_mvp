from app import storage


def test_dedup_first_call_false_then_duplicate_true(temp_db):
    assert storage.message_already_processed("mid-1") is False
    assert storage.message_already_processed("mid-1") is True


def test_dedup_different_ids_are_independent(temp_db):
    assert storage.message_already_processed("mid-1") is False
    assert storage.message_already_processed("mid-2") is False


def test_dedup_empty_id_never_recorded_as_duplicate(temp_db):
    assert storage.message_already_processed("") is False
    assert storage.message_already_processed("") is False


def test_dedup_persists_across_a_fresh_connection(temp_db):
    # Simulates surviving a process restart: every call opens its own
    # connection already, so this just re-asserts persistence explicitly.
    storage.message_already_processed("mid-restart")
    assert storage.message_already_processed("mid-restart") is True


def test_conversation_history_roundtrip_is_chronological(temp_db):
    storage.append_history_turn("psid-A", "user", "hello")
    storage.append_history_turn("psid-A", "assistant", "hi there")

    assert storage.get_recent_history("psid-A") == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi there"},
    ]


def test_conversation_history_isolated_per_sender(temp_db):
    storage.append_history_turn("psid-A", "user", "hello A")
    storage.append_history_turn("psid-B", "user", "hello B")

    assert storage.get_recent_history("psid-A") == [
        {"role": "user", "content": "hello A"}
    ]
    assert storage.get_recent_history("psid-B") == [
        {"role": "user", "content": "hello B"}
    ]


def test_conversation_history_prompt_window_respects_limit(temp_db):
    for i in range(10):
        storage.append_history_turn("psid-C", "user", f"msg-{i}")

    recent = storage.get_recent_history("psid-C", limit=3)

    assert [turn["content"] for turn in recent] == ["msg-7", "msg-8", "msg-9"]


def test_conversation_history_caps_storage_at_20_per_sender(temp_db):
    for i in range(25):
        storage.append_history_turn("psid-D", "user", f"msg-{i}")

    all_kept = storage.get_recent_history("psid-D", limit=100)

    assert len(all_kept) == 20
    assert all_kept[0]["content"] == "msg-5"
    assert all_kept[-1]["content"] == "msg-24"
