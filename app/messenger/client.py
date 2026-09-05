import logging

import httpx

from app.config import PAGE_ACCESS_TOKEN, PAGE_ID


logger = logging.getLogger(__name__)


async def send_message_to_messenger(
    psid: str,
    message_text: str
):

    url = (
        f"https://graph.facebook.com/"
        f"v26.0/{PAGE_ID}/messages"
    )

    payload = {
        "recipient": {
            "id": psid
        },
        "messaging_type": "RESPONSE",
        "message": {
            "text": message_text
        }
    }

    headers = {
        "Authorization": (
            f"Bearer {PAGE_ACCESS_TOKEN}"
        ),
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(
        timeout=20.0
    ) as client:

        response = await client.post(
            url,
            json=payload,
            headers=headers
        )


    logger.info("Meta send status: %s", response.status_code)
    logger.debug("Meta send response: %s", response.text)


    if response.status_code >= 400:
        raise RuntimeError(
            "Meta API error: "
            f"{response.status_code} - "
            f"{response.text}"
        )
