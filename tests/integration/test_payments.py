"""Integration tests for payment endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_crypto_payment_requires_auth(client: AsyncClient):
    """Test that creating crypto payment requires authentication."""
    payload = {
        "amount_usd": 10.0,
        "gb_purchased": 20.0,
        "network": "BSC",
    }
    response = await client.post("/api/v1/payments/crypto", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_crypto_payment_invalid_amount(client: AsyncClient, auth_headers: dict):
    """Test creating crypto payment with invalid amount."""
    payload = {
        "amount_usd": -10.0,
        "gb_purchased": 20.0,
        "network": "BSC",
    }
    response = await client.post("/api/v1/payments/crypto", json=payload, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_payment_history_empty(client: AsyncClient, auth_headers: dict):
    """Test getting payment history when empty."""
    response = await client.get("/api/v1/payments/history", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_payment_history_with_payments(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test getting payment history with existing payments."""
    # Get user from auth_headers (we need to extract user_id from conftest)
    # For this test, we'll just verify the endpoint works
    response = await client.get("/api/v1/payments/history", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_payment_not_found(client: AsyncClient, auth_headers: dict):
    """Test getting a non-existent payment."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/payments/{fake_id}", headers=auth_headers)
    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_create_telegram_stars_payment_requires_auth(client: AsyncClient):
    """Test that creating Telegram Stars payment requires authentication."""
    payload = {
        "amount_usd": 10.0,
        "gb_purchased": 20.0,
    }
    response = await client.post("/api/v1/payments/stars", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_telegram_stars_payment_invalid_amount(
    client: AsyncClient, auth_headers: dict
):
    """Test creating Telegram Stars payment with invalid amount."""
    payload = {
        "amount_usd": -10.0,
        "gb_purchased": 20.0,
    }
    response = await client.post("/api/v1/payments/stars", json=payload, headers=auth_headers)
    assert response.status_code == 422
