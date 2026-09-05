from app.ai.gemini_client import generate_ai_reply
from app.messenger.client import send_message_to_messenger


async def process_message(
    sender_id: str,
    message_text: str,
    message_id: str
):

    try:

        print(
            f"Processing message: {message_id}"
        )

        ai_reply = generate_ai_reply(
            message_text
        )

        print(
            "AI Reply:",
            ai_reply
        )

        await send_message_to_messenger(
            sender_id,
            ai_reply
        )

        print(
            f"Message {message_id} processed successfully."
        )

    except Exception as error:

        print(
            f"Processing error for {message_id}:",
            error
        )

        # Send one fallback response
        try:

            await send_message_to_messenger(
                sender_id,
                "عذرًا، حصلت مشكلة مؤقتة. حاول مرة أخرى."
            )

        except Exception as send_error:

            print(
                "Fallback send error:",
                send_error
            )
