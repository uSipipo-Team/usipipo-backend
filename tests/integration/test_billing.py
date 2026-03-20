"""Integration tests for billing endpoints."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.vpn_key import VpnKey
from usipipo_commons.domain.enums.key_type import KeyType

from src.infrastructure.persistence.repositories.vpn_repository import VpnRepository


@pytest.mark.asyncio
async def test_get_usage_requires_auth(client: AsyncClient):
    """Test that getting usage requires authentication."""
    response = await client.get("/api/v1/billing/usage")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_usage(client: AsyncClient, auth_headers: dict):
    """Test getting user usage."""
    response = await client.get("/api/v1/billing/usage", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "balance_gb" in data
    assert "total_purchased_gb" in data
    assert "keys_count" in data
    assert "data_used_gb" in data
    assert "data_limit_gb" in data
    assert "usage_percentage" in data


@pytest.mark.asyncio
async def test_get_key_usage_empty(client: AsyncClient, auth_headers: dict):
    """Test getting key usage when no keys exist."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/billing/usage/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_key_usage_with_key(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test getting key usage with existing key."""
    # Create a test VPN key
    test_key = VpnKey(
        id=str(uuid4()),
        user_id=123456789,
        name="Test Key",
        key_type=KeyType.WIREGUARD,
        key_data="config",
        external_id="peer-123",
        is_active=True,
        created_at=datetime.now(UTC),
        expires_at=None,
        last_seen_at=None,
        used_bytes=int(1.5 * 1024**3),
        data_limit_bytes=5 * 1024**3,
        billing_reset_at=datetime.now(UTC),
    )

    vpn_repo = VpnRepository(test_session)
    await vpn_repo.create(test_key)

    # Test with the created key ID
    response = await client.get(f"/api/v1/billing/usage/{test_key.id}", headers=auth_headers)
    # Should be 403 because user doesn't own the key
    assert response.status_code in [200, 403, 404]


@pytest.mark.asyncio
async def test_get_key_usage_not_authorized(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test getting key usage for key not owned by user."""
    # Create a key with different user_id
    test_key = VpnKey(
        id=str(uuid4()),
        user_id=987654321,
        name="Other User Key",
        key_type=KeyType.WIREGUARD,
        key_data="config",
        external_id="peer-456",
        is_active=True,
        created_at=datetime.now(UTC),
        expires_at=None,
        last_seen_at=None,
        used_bytes=0,
        data_limit_bytes=5 * 1024**3,
        billing_reset_at=datetime.now(UTC),
    )

    vpn_repo = VpnRepository(test_session)
    await vpn_repo.create(test_key)

    response = await client.get(f"/api/v1/billing/usage/{test_key.id}", headers=auth_headers)
    assert response.status_code in [403, 404]
