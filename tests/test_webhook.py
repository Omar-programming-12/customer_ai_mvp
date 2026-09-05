"""Webhook tests.

receive_webhook fires message processing via asyncio.create_task
(fire-and-forget, by design - it must return to Meta immediately). A
synchronous TestClient.post() can return before that background task has
actually run, so these tests use an async httpx client against the ASGI
app directly and explicitly drain any pending background tasks after each
request before asserting on their effects.
"""

import asyncio
import hashlib
import hmac
import json

import httpx
import pytest
from unittest.mock import patch

import app.main as main_module
from app.config import APP_SECRET
from app.routes import webhook as webhook_module


def _signed(body: bytes, secret: str = APP_SECRET) -> dict:
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return {"X-Hub-Signature-256": signature}


def _payload(mid: str, text: str = "hi", sender: str = "psid-1") -> bytes:
    return json.dumps({
        "entry": [{
            "messaging": [{
                "sender": {"id": sender},
                "message": {"text": text, "mid": mid},
            }]
        }]
    }).encode()


async def _drain_background_tasks():
    """Let any asyncio.create_task(...) spawned by the request just
    handled actually finish, before the caller asserts on its effects."""

    pending = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]

    if pending:
        await asyncio.gather(*pending)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    webhook_module._recent_message_times.clear()
    yield
    webhook_module._recent_message_times.clear()


@pytest.fixture
async def client(temp_db):
    transport = httpx.ASGITransport(app=main_module.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


async def test_valid_signature_is_accepted(client):
    body = _payload("mid-ok")
    with patch("app.services.message_processor.generate_ai_reply", return_value="ok"), \
         patch("app.services.message_processor.send_message_to_messenger"):
        response = await client.post("/webhook", content=body, headers=_signed(body))
        await _drain_background_tasks()
    assert response.status_code == 200


async def test_wrong_secret_is_rejected(client):
    body = _payload("mid-bad")
    response = await client.post("/webhook", content=body, headers=_signed(body, secret="wrong-secret"))
    assert response.status_code == 403


async def test_missing_signature_is_rejected(client):
    body = _payload("mid-missing")
    response = await client.post("/webhook", content=body)
    assert response.status_code == 403


async def test_malformed_signature_header_is_rejected(client):
    body = _payload("mid-malformed")
    response = await client.post("/webhook", content=body, headers={"X-Hub-Signature-256": "garbage"})
    assert response.status_code == 403


async def test_oversized_message_is_truncated_before_processing(client):
    long_text = "أ" * 5000
    body = _payload("mid-long", text=long_text)
    received = []

    def fake_generate(text, history=None):
        received.append(text)
        return "ok"

    with patch("app.services.message_processor.generate_ai_reply", side_effect=fake_generate), \
         patch("app.services.message_processor.send_message_to_messenger"):
        await client.post("/webhook", content=body, headers=_signed(body))
        await _drain_background_tasks()

    assert len(received[0]) == webhook_module._MAX_MESSAGE_LENGTH


async def test_rate_limit_caps_processing_per_sender(client):
    with patch("app.services.message_processor.generate_ai_reply", return_value="ok") as fake_reply, \
         patch("app.services.message_processor.send_message_to_messenger"):
        for i in range(webhook_module._RATE_LIMIT_MAX_MESSAGES + 2):
            body = _payload(f"mid-rl-{i}", sender="psid-ratelimited")
            response = await client.post("/webhook", content=body, headers=_signed(body))
            assert response.status_code == 200
        await _drain_background_tasks()

    assert fake_reply.call_count == webhook_module._RATE_LIMIT_MAX_MESSAGES


async def test_duplicate_message_id_is_processed_only_once(client):
    body = _payload("mid-dup")
    with patch("app.services.message_processor.generate_ai_reply", return_value="ok") as fake_reply, \
         patch("app.services.message_processor.send_message_to_messenger"):
        await client.post("/webhook", content=body, headers=_signed(body))
        await client.post("/webhook", content=body, headers=_signed(body))
        await _drain_background_tasks()

    assert fake_reply.call_count == 1
