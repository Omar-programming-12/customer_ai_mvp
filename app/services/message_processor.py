import asyncio
import logging

from app.ai import memory
from app.ai.gemini_client import generate_ai_reply
from app.messenger.client import send_message_to_messenger


logger = logging.getLogger(__name__)


async def process_message(
    sender_id: str,
    message_text: str,
    message_id: str
):

    try:

        logger.info("Processing message: %s", message_id)

        # Blocking SQLite I/O - same reasoning as generate_ai_reply below.
        history = await asyncio.to_thread(memory.get_history, sender_id)

        # generate_ai_reply does blocking network I/O (Gemini embeddings,
        # Groq chat/tool calls) - run it off the event loop so one slow
        # reply doesn't stall every other request this process is
        # handling concurrently.
        ai_reply = await asyncio.to_thread(
            generate_ai_reply,
            message_text,
            history,
        )

        # generate_ai_reply returns None for a meaningless/non-actionable
        # message (see app.ai.router.Route.MEANINGLESS) - the classification
        # itself lives entirely in the routing layer; this is just the
        # generation-layer contract's other valid outcome besides a string,
        # not a new decision made here. The message was already logged
        # above (and by the webhook before this call); there's simply
        # nothing to send back or record as a conversation turn.
        if ai_reply is None:
            logger.info("No reply for %s (meaningless/non-actionable message).", message_id)
            return

        logger.info("AI reply for %s: %s", message_id, ai_reply)

        await send_message_to_messenger(
            sender_id,
            ai_reply
        )

        # Recorded only after a successful send, so a failed turn (caught
        # below) doesn't leave a half-answered exchange in history for the
        # next message to be confused by.
        await asyncio.to_thread(memory.remember, sender_id, "user", message_text)
        await asyncio.to_thread(memory.remember, sender_id, "assistant", ai_reply)

        logger.info("Message %s processed successfully.", message_id)

    except Exception:

        logger.exception("Processing error for %s", message_id)

        # Send one fallback response
        try:

            await send_message_to_messenger(
                sender_id,
                "عذرًا، حصلت مشكلة مؤقتة. حاول مرة أخرى."
            )

        except Exception:

            logger.exception("Fallback send error for %s", message_id)
