"""Tests de integración para los endpoints de referidos."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.user import User

from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.shared.security.jwt import create_jwt_token


@pytest.mark.asyncio
async def test_get_referral_stats(client: AsyncClient, auth_headers: dict):
    """Test obtener estadísticas de referidos."""
    response = await client.get("/api/v1/referrals/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "referral_code" in data
    assert data["total_referrals"] == 0


@pytest.mark.asyncio
async def test_apply_referral_code_integration(client: AsyncClient, test_session: AsyncSession):
    """Test flujo de aplicar un código de referido."""
    user_repo = UserRepository(test_session)

    # 1. Crear un usuario referidor con un código conocido
    referrer_id = uuid4()
    referrer = User(
        id=referrer_id,
        telegram_id=999,
        username="referrer",
        first_name="R",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="PROMO2024",
        referred_by=None,
    )
    await user_repo.create(referrer)

    # 2. Crear un usuario nuevo (el que aplicará el código)
    new_user_id = uuid4()
    new_user = User(
        id=new_user_id,
        telegram_id=888,
        username="new_user",
        first_name="N",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="NEW888",
        referred_by=None,
    )
    await user_repo.create(new_user)

    # 3. Autenticar como el usuario nuevo
    token = create_jwt_token(new_user_id, 888)
    headers = {"Authorization": f"Bearer {token}"}

    # 4. Aplicar código
    response = await client.post(
        "/api/v1/referrals/apply", json={"referral_code": "PROMO2024"}, headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    # 5. Verificar que se asignaron créditos
    response_stats = await client.get("/api/v1/referrals/me", headers=headers)
    assert response_stats.json()["referral_credits"] > 0
    assert response_stats.json()["referred_by"] == str(referrer_id)


@pytest.mark.asyncio
async def test_redeem_credits_integration(client: AsyncClient, test_session: AsyncSession):
    """Test canje de créditos por GB."""
    user_repo = UserRepository(test_session)
    user_id = uuid4()
    user = User(
        id=user_id,
        telegram_id=777,
        username="lucky",
        first_name="L",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="LUCKY7",
        referred_by=None,
        referral_credits=500,
    )
    await user_repo.create(user)

    token = create_jwt_token(user_id, 777)
    headers = {"Authorization": f"Bearer {token}"}

    # Canjear 100 créditos por 1GB
    response = await client.post("/api/v1/referrals/redeem", json={"credits": 100}, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    # Verificar balance de GB
    # (El mock original de User en conftest tiene 5.0, aquí creamos uno con 5.0 y sumamos 1.0)
    response_stats = await client.get("/api/v1/referrals/me", headers=headers)
    assert response_stats.json()["referral_credits"] == 400
