"""Integration tests for webhook endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_crypto_webhook_missing_signature(client: AsyncClient):
    """Test crypto webhook without signature header."""
    response = await client.post("/api/v1/webhooks/crypto", json={})
    assert response.status_code == 422  # Missing required header


@pytest.mark.asyncio
async def test_crypto_webhook_invalid_signature(client: AsyncClient):
    """Test crypto webhook with invalid signature."""
    response = await client.post(
        "/api/v1/webhooks/crypto",
        json={"status": "completed"},
        headers={"X-Signature": "invalid-signature"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_telegram_stars_webhook_invalid_payload(client: AsyncClient):
    """Test Telegram Stars webhook with invalid payload."""
    payload = {
        "pre_checkout_query": {
            "id": "test_query_id",
            "invoice_payload": "invalid_format",  # Should start with "user_"
        }
    }
    response = await client.post("/api/v1/webhooks/telegram-stars", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"


@pytest.mark.asyncio
async def test_telegram_stars_webhook_valid_pre_checkout(client: AsyncClient):
    """Test Telegram Stars webhook with valid pre-checkout query."""
    payload = {
        "pre_checkout_query": {
            "id": "test_query_id",
            "invoice_payload": "user_123456",  # Valid format
        }
    }
    response = await client.post("/api/v1/webhooks/telegram-stars", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_telegram_stars_webhook_successful_payment(client: AsyncClient):
    """Test Telegram Stars webhook with successful payment."""
    payload = {
        "message": {
            "from": {"id": 123456},
            "successful_payment": {
                "total_amount": 500,  # 500 stars
                "invoice_payload": "user_123456",
            },
        }
    }
    response = await client.post("/api/v1/webhooks/telegram-stars", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_telegram_stars_webhook_ignored(client: AsyncClient):
    """Test Telegram Stars webhook with ignored update."""
    payload = {"update_id": 12345}  # Not a recognized update type
    response = await client.post("/api/v1/webhooks/telegram-stars", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ignored"
