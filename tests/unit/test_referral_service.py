"""Tests unitarios para ReferralService."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from usipipo_commons.domain.entities.user import User

from src.core.application.services.referral_service import ReferralService


@pytest.fixture
def mock_referral_repo():
    return AsyncMock()


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def referral_service(mock_user_repo, mock_referral_repo):
    return ReferralService(mock_user_repo, mock_referral_repo)


@pytest.mark.asyncio
async def test_register_referral_success(referral_service, mock_user_repo, mock_referral_repo):
    """Test registro de referido exitoso."""
    referrer_id = uuid.uuid4()
    new_user_id = uuid.uuid4()

    referrer = User(
        id=referrer_id,
        telegram_id=1,
        username="ref",
        first_name="R",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )
    new_user = User(
        id=new_user_id,
        telegram_id=2,
        username="new",
        first_name="N",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="NEW456",
        referred_by=None,
    )

    # Mocks
    mock_user_repo.get_by_referral_code.return_value = referrer
    mock_user_repo.get_by_id.return_value = new_user
    mock_referral_repo.save.return_value = AsyncMock()

    result = await referral_service.register_referral(new_user_id, "REF123")

    assert result["success"] is True
    assert result["referrer_id"] == referrer_id

    # Verificar que se actualizaron los usuarios (referente y nuevo usuario)
    assert new_user.referred_by == referrer_id
    assert mock_user_repo.update.call_count == 2


@pytest.mark.asyncio
async def test_redeem_credits_for_data_success(referral_service, mock_user_repo):
    """Test canje de créditos por datos."""
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        telegram_id=1,
        username="u",
        first_name="U",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="U",
        referred_by=None,
        referral_credits=200,
    )

    mock_user_repo.get_by_id.return_value = user

    # Canjear 100 créditos (suponiendo que settings.REFERRAL_CREDITS_PER_GB = 100)
    result = await referral_service.redeem_credits_for_data(user_id, 100)

    assert result["success"] is True
    assert result["gb_added"] == 1
    assert user.balance_gb == 6.0
    assert user.referral_credits == 100
    mock_user_repo.update.assert_called_once()
