import asyncio

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from app.config import VERIFY_TOKEN
from app.messenger.dedup import already_processed
from app.services.message_processor import process_message


router = APIRouter()


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

        print(
            "Webhook verification successful"
        )

        return PlainTextResponse(
            challenge
        )


    print(
        "Webhook verification failed"
    )

    return PlainTextResponse(
        "Verification failed",
        status_code=403
    )


@router.post("/webhook")
async def receive_webhook(
    request: Request
):

    data = await request.json()

    print(
        "\n========== META WEBHOOK =========="
    )

    print(data)


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


            print(
                "Sender PSID:",
                sender_id
            )

            print(
                "Message:",
                message_text
            )

            print(
                "Message ID:",
                message_id
            )


            if not sender_id:
                continue


            if not message_text:
                continue


            if already_processed(message_id):

                print(
                    "Duplicate message ignored:",
                    message_id
                )

                continue


            asyncio.create_task(
                process_message(
                    sender_id=sender_id,
                    message_text=message_text,
                    message_id=message_id
                )
            )


    print(
        "Webhook received successfully."
    )

    print(
        "==================================\n"
    )


    # Return immediately to Meta
    return {
        "status": "received"
    }
