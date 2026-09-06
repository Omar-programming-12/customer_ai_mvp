"""Message dedup, backed by app.storage (SQLite) instead of an in-memory
set, so a duplicate Meta redelivery is still caught after a process
restart or across multiple workers sharing the same DB file - the
in-memory set could do neither.
"""

from app.storage import message_already_processed as already_processed
