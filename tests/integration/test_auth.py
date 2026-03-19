"""Tests de integración para autenticación."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_telegram_invalid_data(client: AsyncClient):
    """Test de autenticación con datos inválidos."""
    response = await client.post(
        "/api/v1/auth/telegram",
        json={"init_data": "invalid_data"},
    )
    assert response.status_code == 401
    assert "Invalid Telegram initData" in response.json()["detail"]


@pytest.mark.asyncio
async def test_auth_telegram_missing_init_data(client: AsyncClient):
    """Test de autenticación sin init_data."""
    response = await client.post(
        "/api/v1/auth/telegram",
        json={},
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test del endpoint root."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test del health check."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
