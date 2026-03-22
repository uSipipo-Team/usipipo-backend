"""Tests unitarios para ReferralRepository."""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.referral import Referral
from usipipo_commons.domain.entities.user import User

from src.infrastructure.persistence.repositories.referral_repository import ReferralRepository
from src.infrastructure.persistence.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_save_and_get_referral(test_session: AsyncSession):
    """Test guardar y obtener una relación de referido."""
    user_repo = UserRepository(test_session)
    referral_repo = ReferralRepository(test_session)

    # 1. Crear usuarios
    u1_id, u2_id = uuid.uuid4(), uuid.uuid4()
    user1 = User(
        id=u1_id,
        telegram_id=1,
        username="u1",
        first_name="R1",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF1",
        referred_by=None,
    )
    user2 = User(
        id=u2_id,
        telegram_id=2,
        username="u2",
        first_name="R2",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF2",
        referred_by=None,
    )
    await user_repo.create(user1)
    await user_repo.create(user2)

    # 2. Crear referido
    referral = Referral(referrer_id=u1_id, referred_id=u2_id)
    saved = await referral_repo.save(referral)
    assert saved.id is not None

    # 3. Obtener
    retrieved = await referral_repo.get_by_referred_id(u2_id)
    assert retrieved is not None
    assert retrieved.referrer_id == u1_id
    assert retrieved.referred_id == u2_id


@pytest.mark.asyncio
async def test_count_referrals(test_session: AsyncSession):
    """Test contar referidos de un usuario."""
    user_repo = UserRepository(test_session)
    referral_repo = ReferralRepository(test_session)

    referrer_id = uuid.uuid4()
    referrer = User(
        id=referrer_id,
        telegram_id=100,
        username="ref",
        first_name="R",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="MAIN",
        referred_by=None,
    )
    await user_repo.create(referrer)

    for i in range(3):
        u_id = uuid.uuid4()
        u = User(
            id=u_id,
            telegram_id=200 + i,
            username=f"u{i}",
            first_name="U",
            last_name="",
            is_admin=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            balance_gb=5.0,
            total_purchased_gb=0.0,
            referral_code=f"R{i}",
            referred_by=None,
        )
        await user_repo.create(u)
        await referral_repo.save(Referral(referrer_id=referrer_id, referred_id=u_id))

    count = await referral_repo.count_referrals_by_referrer(referrer_id)
    assert count == 3


@pytest.mark.asyncio
async def test_mark_bonus_applied(test_session: AsyncSession):
    """Test marcar bono de referido como aplicado."""
    user_repo = UserRepository(test_session)
    referral_repo = ReferralRepository(test_session)

    u1_id, u2_id = uuid.uuid4(), uuid.uuid4()
    await user_repo.create(
        User(
            id=u1_id,
            telegram_id=1,
            username="u1",
            first_name="R1",
            last_name="",
            is_admin=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            balance_gb=5.0,
            total_purchased_gb=0.0,
            referral_code="REF1",
            referred_by=None,
        )
    )
    await user_repo.create(
        User(
            id=u2_id,
            telegram_id=2,
            username="u2",
            first_name="R2",
            last_name="",
            is_admin=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            balance_gb=5.0,
            total_purchased_gb=0.0,
            referral_code="REF2",
            referred_by=None,
        )
    )

    referral = Referral(referrer_id=u1_id, referred_id=u2_id)
    saved = await referral_repo.save(referral)
    assert saved.bonus_applied is False

    success = await referral_repo.mark_bonus_applied(saved.id)
    assert success is True

    updated = await referral_repo.get_by_id(saved.id)
    assert updated is not None
    assert updated.bonus_applied is True
