import asyncio
import hashlib
import hmac
import json
import logging
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from app.config import APP_SECRET, VERIFY_TOKEN
from app.messenger.dedup import already_processed
from app.services.message_processor import process_message


logger = logging.getLogger(__name__)

router = APIRouter()

# A message longer than this is truncated before processing - protects
# against a single oversized message driving up embedding/generation
# token cost (and by extension, Gemini/Groq spend) far beyond what any
# genuine customer question needs.
_MAX_MESSAGE_LENGTH = 2000

# Soft, best-effort abuse protection per sender. In-memory and per
# process/worker (same tradeoff as any in-process cache) - it won't catch
# a distributed attacker spread across many workers, but it does stop a
# single sender from burning API budget through this one worker, without
# needing a shared store for what is a defense-in-depth measure, not a
# correctness requirement.
_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_MESSAGES = 10

_recent_message_times: dict[str, deque] = defaultdict(deque)


def _is_rate_limited(sender_id: str) -> bool:

    now = time.monotonic()
    timestamps = _recent_message_times[sender_id]

    while timestamps and now - timestamps[0] > _RATE_LIMIT_WINDOW_SECONDS:
        timestamps.popleft()

    if len(timestamps) >= _RATE_LIMIT_MAX_MESSAGES:
        return True

    timestamps.append(now)

    return False


def _has_valid_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Verify Meta's X-Hub-Signature-256 header: HMAC-SHA256 of the exact
    raw request body, keyed with the App Secret. Must run against the raw
    bytes, not a re-serialized/re-parsed version of the JSON - any
    formatting difference would break the signature even for a genuine
    request."""

    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected_signature = signature_header.removeprefix("sha256=")

    computed_signature = hmac.new(
        APP_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed_signature, expected_signature)


@router.get("/webhook")
async def verify_webhook(
    request: Request
):

    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")


    if (
        mode == "subscribe"
        and token == VERIFY_TOKEN
        and challenge
    ):

        logger.info("Webhook verification successful")

        return PlainTextResponse(
            challenge
        )


    logger.warning("Webhook verification failed")

    return PlainTextResponse(
        "Verification failed",
        status_code=403
    )


@router.post("/webhook")
async def receive_webhook(
    request: Request
):

    raw_body = await request.body()

    if not _has_valid_signature(raw_body, request.headers.get("X-Hub-Signature-256")):

        logger.warning("Webhook signature verification failed")

        return PlainTextResponse(
            "Invalid signature",
            status_code=403
        )

    data = json.loads(raw_body)

    logger.info("Received Meta webhook payload")
    logger.debug("Webhook payload: %s", data)


    for entry in data.get("entry", []):

        for event in entry.get(
            "messaging",
            []
        ):

            sender = event.get(
                "sender",
                {}
            )

            message = event.get(
                "message",
                {}
            )

            sender_id = sender.get("id")
            message_text = message.get("text")
            message_id = message.get("mid")

            logger.info(
                "Incoming message id=%s sender=%s", message_id, sender_id
            )


            if not sender_id:
                continue


            if not message_text:
                continue


            if _is_rate_limited(sender_id):

                logger.warning("Rate limit exceeded for sender %s", sender_id)

                continue


            if len(message_text) > _MAX_MESSAGE_LENGTH:

                logger.warning(
                    "Truncating oversized message (%d chars) from %s",
                    len(message_text), sender_id,
                )

                message_text = message_text[:_MAX_MESSAGE_LENGTH]


            # already_processed does blocking SQLite I/O - keep it off the
            # event loop, same as any other blocking call in this app.
            if await asyncio.to_thread(already_processed, message_id):

                logger.info("Duplicate message ignored: %s", message_id)

                continue


            asyncio.create_task(
                process_message(
                    sender_id=sender_id,
                    message_text=message_text,
                    message_id=message_id
                )
            )


    logger.info("Webhook processed")


    # Return immediately to Meta
    return {
        "status": "received"
    }
