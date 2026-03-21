"""Tests unitarios para DataPackageService."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from usipipo_commons.domain.entities.user import User

from src.core.application.services.data_package_service import DataPackageService


@pytest.fixture
def mock_package_repo():
    return AsyncMock()


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def data_package_service(mock_package_repo, mock_user_repo):
    return DataPackageService(mock_package_repo, mock_user_repo)


@pytest.mark.asyncio
async def test_purchase_package_success(data_package_service, mock_package_repo, mock_user_repo):
    """Test compra exitosa de un paquete."""
    telegram_id = 123
    user = User(
        id=uuid.uuid4(),
        telegram_id=telegram_id,
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

    mock_user_repo.get_by_telegram_id = AsyncMock(return_value=user)
    mock_package_repo.get_valid_by_user.return_value = []
    mock_package_repo.save.side_effect = lambda pkg, _: pkg  # Retorna el mismo objeto

    package, bonuses = await data_package_service.purchase_package(
        telegram_id=telegram_id,
        package_type="basic",
        telegram_payment_id="pay_abc",
        current_user_id=telegram_id,
    )

    assert package.user_id == telegram_id
    assert package.telegram_payment_id == "pay_abc"
    assert bonuses["total_bonus_percent"] >= 0

    # Verificar que se actualizó el usuario
    assert user.purchase_count == 1
    assert user.welcome_bonus_used is True
    mock_user_repo.update.assert_called_once()
