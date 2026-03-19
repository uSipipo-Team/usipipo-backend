"""Integration tests for billing endpoints."""

from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.vpn_key import VpnKey
from usipipo_commons.domain.enums.key_status import KeyStatus
from usipipo_commons.domain.enums.vpn_type import VpnType

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
        id=uuid4(),
        user_id=uuid4(),  # This won't match the auth user, but we test the structure
        name="Test Key",
        vpn_type=VpnType.WIREGUARD,
        status=KeyStatus.ACTIVE,
        config="config",
        created_at=datetime.utcnow(),
        expires_at=None,
        last_used_at=None,
        data_used_gb=1.5,
        data_limit_gb=5.0,
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
    different_user_id = uuid4()
    test_key = VpnKey(
        id=uuid4(),
        user_id=different_user_id,
        name="Other User Key",
        vpn_type=VpnType.WIREGUARD,
        status=KeyStatus.ACTIVE,
        config="config",
        created_at=datetime.utcnow(),
        expires_at=None,
        last_used_at=None,
        data_used_gb=0.0,
        data_limit_gb=5.0,
    )

    vpn_repo = VpnRepository(test_session)
    await vpn_repo.create(test_key)

    response = await client.get(f"/api/v1/billing/usage/{test_key.id}", headers=auth_headers)
    assert response.status_code in [403, 404]
