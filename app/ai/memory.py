"""Per-sender conversation history, backed by app.storage (SQLite).

Deliberately small for this phase: a short rolling window of raw
(role, content) turns per sender, prepended to the Groq message list so a
follow-up like "وكام سعره؟" can be understood using the previous turn's
context instead of being evaluated in isolation.

Routing (app.ai.router) does NOT consult this yet - it still classifies
each message independently. A short/ambiguous follow-up can therefore
still land on out_of_scope before generation (and its history) ever gets
a chance to help. This is a known, deliberate scope boundary for the
first version, not an oversight - making routing itself context-aware is
a larger, separate change to the calibrated confidence thresholds.
"""

from app.storage import append_history_turn, get_recent_history


# Turns sent to Groq as prior context - kept small to bound prompt size/
# cost; enough for the immediate "what were we just talking about"
# follow-ups this phase targets, not a long-running conversation summary.
_HISTORY_TURNS_FOR_PROMPT = 6


def get_history(sender_id: str) -> list[dict]:

    return get_recent_history(sender_id, limit=_HISTORY_TURNS_FOR_PROMPT)


def remember(sender_id: str, role: str, content: str) -> None:

    append_history_turn(sender_id, role, content)
