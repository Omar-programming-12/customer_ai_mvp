"""Local SQLite-backed runtime state.

One small file-based store instead of separate in-memory structures per
concern: it backs message dedup (app.messenger.dedup) and per-sender
conversation history (app.ai.memory) - both are "small per-key state that
must survive a restart", which is exactly what SQLite is for at this
project's scale. No server process, no extra dependency (sqlite3 is in
the standard library).

Every function here does blocking file I/O - callers in async code must
wrap calls in asyncio.to_thread (see app.routes.webhook), the same as any
other blocking call in this app (Gemini/Groq requests).
"""

import sqlite3
from contextlib import contextmanager

from app import config


@contextmanager
def _connect():

    # Read config.DB_PATH at call time (not bound at import time) so
    # tests can point it at a temp file per test via monkeypatch.
    db_path = config.DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)

    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    """Create tables if they don't exist yet. Safe to call on every
    startup - CREATE TABLE IF NOT EXISTS is idempotent."""

    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_messages (
                message_id TEXT PRIMARY KEY,
                processed_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_conversation_history_sender "
            "ON conversation_history (sender_id, id)"
        )


# Meta's own redelivery window for a webhook event is measured in
# minutes, not days - keeping a week of history is generous headroom
# while still bounding table growth without needing a separate cleanup
# job or scheduler.
_DEDUP_RETENTION_DAYS = 7


def message_already_processed(message_id: str) -> bool:
    """True if message_id was already seen; otherwise records it and
    returns False. Uses INSERT OR IGNORE against the message_id primary
    key rather than a separate SELECT-then-INSERT, so the check-and-record
    is a single atomic statement - safe even against two near-simultaneous
    calls for the same id, which a read-then-write pair would not be."""

    if not message_id:
        return False

    with _connect() as connection:

        cursor = connection.execute(
            "INSERT OR IGNORE INTO processed_messages (message_id) VALUES (?)",
            (message_id,),
        )

        already_seen = cursor.rowcount == 0

        connection.execute(
            "DELETE FROM processed_messages "
            "WHERE processed_at < datetime('now', ?)",
            (f"-{_DEDUP_RETENTION_DAYS} days",),
        )

    return already_seen


# Bounds each sender's history independently of how long they've been
# chatting - a very active sender can't grow their own row count without
# limit, and a quiet one never gets swept out early by a global cap.
_HISTORY_MAX_TURNS_PER_SENDER = 20


def append_history_turn(sender_id: str, role: str, content: str) -> None:
    """Record one turn (role: "user" or "assistant") and trim that
    sender's history down to the most recent _HISTORY_MAX_TURNS_PER_SENDER
    rows, so per-sender storage stays bounded regardless of how long a
    conversation runs."""

    with _connect() as connection:

        connection.execute(
            "INSERT INTO conversation_history (sender_id, role, content) VALUES (?, ?, ?)",
            (sender_id, role, content),
        )

        connection.execute(
            """
            DELETE FROM conversation_history
            WHERE sender_id = ? AND id NOT IN (
                SELECT id FROM conversation_history
                WHERE sender_id = ?
                ORDER BY id DESC
                LIMIT ?
            )
            """,
            (sender_id, sender_id, _HISTORY_MAX_TURNS_PER_SENDER),
        )


def get_recent_history(sender_id: str, limit: int = 6) -> list[dict]:
    """Most recent `limit` turns for sender_id, oldest first (the order a
    chat prompt expects) - the opposite of the ORDER BY used to fetch
    them, which needs newest-first to LIMIT correctly."""

    with _connect() as connection:

        cursor = connection.execute(
            "SELECT role, content FROM conversation_history "
            "WHERE sender_id = ? ORDER BY id DESC LIMIT ?",
            (sender_id, limit),
        )

        rows = cursor.fetchall()

    rows.reverse()

    return [{"role": role, "content": content} for role, content in rows]
