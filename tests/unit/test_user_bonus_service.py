"""Tests unitarios para UserBonusService."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from usipipo_commons.domain.entities.data_package import DataPackage, PackageType
from usipipo_commons.domain.entities.user import User

from src.core.application.services.user_bonus_service import UserBonusService


@pytest.fixture
def bonus_service():
    return UserBonusService()


@pytest.fixture
def base_user():
    return User(
        id=uuid4(),
        telegram_id=123,
        username="test",
        first_name="Test",
        last_name="User",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )


def test_welcome_bonus(bonus_service, base_user):
    """Test bono de bienvenida en primera compra."""
    base_user.purchase_count = 0
    base_user.welcome_bonus_used = False

    bonus = bonus_service.calculate_welcome_bonus(base_user)
    assert bonus.percent == bonus_service.WELCOME_BONUS_PERCENT
    assert "Bienvenida" in bonus.description


def test_loyalty_bonus(bonus_service, base_user):
    """Test bono de lealtad."""
    base_user.loyalty_bonus_percent = 10

    bonus = bonus_service.calculate_loyalty_bonus(base_user)
    assert bonus.percent == 10
    assert "Fidelidad" in bonus.description


def test_quick_renewal_bonus(bonus_service, base_user):
    """Test bono por renovación rápida."""
    # Paquete que vence en 3 días
    pkg = DataPackage(
        user_id=base_user.telegram_id,
        package_type=PackageType.BASIC,
        data_limit_bytes=10**9,
        stars_paid=250,
        expires_at=datetime.now(UTC) + timedelta(days=3),
    )

    bonus = bonus_service.calculate_quick_renewal_bonus(base_user, [pkg])
    assert bonus.percent == bonus_service.QUICK_RENEWAL_BONUS_PERCENT
    assert "Rápida" in bonus.description


def test_total_bonus_calculation(bonus_service, base_user):
    """Test cálculo total de bonos acumulados."""
    base_user.purchase_count = 0  # Welcome (+20%)
    base_user.loyalty_bonus_percent = 5  # Loyalty (+5%)

    # Quick renewal (+15%)
    pkg = DataPackage(
        user_id=base_user.telegram_id,
        package_type=PackageType.BASIC,
        data_limit_bytes=10**9,
        stars_paid=250,
        expires_at=datetime.now(UTC) + timedelta(days=2),
    )

    total_percent, bonuses = bonus_service.calculate_total_bonus(
        base_user,
        [pkg],
        is_referred_user_first_purchase=True,  # (+10%)
    )

    # 20 + 5 + 15 + 10 = 50%
    assert total_percent == 50
    assert len(bonuses) == 4
