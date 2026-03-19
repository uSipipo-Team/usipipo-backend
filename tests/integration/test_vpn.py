"""Tests de integración para VPN."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_vpn_keys_requires_auth(client: AsyncClient):
    """Test que lista de claves VPN requiere autenticación."""
    response = await client.get("/api/v1/vpn/keys")
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_create_vpn_key_requires_auth(client: AsyncClient):
    """Test que crear clave VPN requiere autenticación."""
    payload = {
        "name": "My VPN",
        "vpn_type": "wireguard",
        "data_limit_gb": 5.0,
    }
    response = await client.post("/api/v1/vpn/keys", json=payload)
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_get_vpn_key_requires_auth(client: AsyncClient):
    """Test que obtener clave VPN requiere autenticación."""
    response = await client.get("/api/v1/vpn/keys/some-uuid")
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_delete_vpn_key_requires_auth(client: AsyncClient):
    """Test que eliminar clave VPN requiere autenticación."""
    response = await client.delete("/api/v1/vpn/keys/some-uuid")
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_update_vpn_key_requires_auth(client: AsyncClient):
    """Test que actualizar clave VPN requiere autenticación."""
    payload = {"name": "Updated Name"}
    response = await client.put(
        "/api/v1/vpn/keys/some-uuid",
        json=payload,
    )
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_create_vpn_key_invalid_type(client: AsyncClient, auth_headers: dict):
    """Test de creación de clave VPN con tipo inválido."""
    payload = {
        "name": "My VPN",
        "vpn_type": "invalid_type",
        "data_limit_gb": 5.0,
    }
    response = await client.post(
        "/api/v1/vpn/keys",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_vpn_keys_with_auth(client: AsyncClient, auth_headers: dict):
    """Test de lista de claves VPN con autenticación (lista vacía)."""
    with (
        patch("src.infrastructure.api.v1.deps.OutlineClient"),
        patch("src.infrastructure.api.v1.deps.WireGuardClient"),
    ):
        response = await client.get(
            "/api/v1/vpn/keys",
            headers=auth_headers,
        )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_vpn_key_success(client: AsyncClient, auth_headers: dict):
    """Test de creación exitosa de clave VPN."""
    payload = {
        "name": "My VPN",
        "vpn_type": "wireguard",
        "data_limit_gb": 5.0,
    }

    # Mock para evitar acceso a /etc/wireguard
    mock_wg_client = AsyncMock()
    mock_wg_client.create_peer.return_value = {
        "id": "test-pub-key",
        "name": "My VPN",
        "client_name": "wg-test-123",
        "ip": "10.0.0.2",
        "config": "[Interface]\nPrivateKey = test\n[Peer]\nPublicKey = test",
        "file_path": "/tmp/test.conf",
    }

    with (
        patch("src.infrastructure.api.v1.deps.OutlineClient"),
        patch("src.infrastructure.api.v1.deps.WireGuardClient", return_value=mock_wg_client),
    ):
        response = await client.post(
            "/api/v1/vpn/keys",
            json=payload,
            headers=auth_headers,
        )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My VPN"
    assert data["vpn_type"] == "wireguard"
    assert "id" in data
    assert "user_id" in data
    assert "config" in data


@pytest.mark.asyncio
async def test_auth_telegram_invalid_data(client: AsyncClient):
    """Test de autenticación con datos inválidos."""
    response = await client.post(
        "/api/v1/auth/telegram",
        json={"init_data": "invalid_data"},
    )
    assert response.status_code == 401
    assert "Invalid Telegram initData" in response.json()["detail"]
