"""Tests unitarios para DataPackageRepository."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.data_package import DataPackage, PackageType
from usipipo_commons.domain.entities.user import User

from src.infrastructure.persistence.repositories.data_package_repository import (
    DataPackageRepository,
)
from src.infrastructure.persistence.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_save_and_get_data_package(test_session: AsyncSession):
    """Test guardar y obtener un paquete de datos."""
    # 1. Crear usuario previo (necesario por FK)
    user_repo = UserRepository(test_session)
    test_user = User(
        id=uuid.uuid4(),
        telegram_id=12345,
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
    await user_repo.create(test_user)

    # 2. Crear paquete
    repo = DataPackageRepository(test_session)
    package = DataPackage(
        user_id=12345,
        package_type=PackageType.BASIC,
        data_limit_bytes=10 * 1024**3,
        stars_paid=250,
        expires_at=datetime.now(UTC) + timedelta(days=30),
        telegram_payment_id="pay_123",
    )

    # Guardar
    saved = await repo.save(package, 12345)
    assert saved.id is not None
    assert saved.telegram_payment_id == "pay_123"

    # Obtener por ID
    retrieved = await repo.get_by_id(saved.id, 12345)
    assert retrieved is not None
    assert retrieved.user_id == 12345
    assert retrieved.package_type == PackageType.BASIC


@pytest.mark.asyncio
async def test_get_valid_by_user(test_session: AsyncSession):
    """Test obtener paquetes válidos de un usuario."""
    user_repo = UserRepository(test_session)
    telegram_id = 55555
    test_user = User(
        id=uuid.uuid4(),
        telegram_id=telegram_id,
        username="test2",
        first_name="Test",
        last_name="User",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF555",
        referred_by=None,
    )
    await user_repo.create(test_user)

    repo = DataPackageRepository(test_session)

    # Paquete válido
    p1 = DataPackage(
        user_id=telegram_id,
        package_type=PackageType.BASIC,
        data_limit_bytes=10 * 1024**3,
        stars_paid=250,
        expires_at=datetime.now(UTC) + timedelta(days=30),
        is_active=True,
    )

    # Paquete expirado
    p2 = DataPackage(
        user_id=telegram_id,
        package_type=PackageType.BASIC,
        data_limit_bytes=10 * 1024**3,
        stars_paid=250,
        expires_at=datetime.now(UTC) - timedelta(days=1),
        is_active=True,
    )

    # Paquete inactivo
    p3 = DataPackage(
        user_id=telegram_id,
        package_type=PackageType.BASIC,
        data_limit_bytes=10 * 1024**3,
        stars_paid=250,
        expires_at=datetime.now(UTC) + timedelta(days=30),
        is_active=False,
    )

    await repo.save(p1, telegram_id)
    await repo.save(p2, telegram_id)
    await repo.save(p3, telegram_id)

    valid_packages = await repo.get_valid_by_user(telegram_id, telegram_id)

    assert len(valid_packages) == 1
    assert valid_packages[0].id == p1.id


@pytest.mark.asyncio
async def test_update_usage(test_session: AsyncSession):
    """Test actualizar uso de datos en un paquete."""
    user_repo = UserRepository(test_session)
    telegram_id = 777
    test_user = User(
        id=uuid.uuid4(),
        telegram_id=telegram_id,
        username="test3",
        first_name="Test",
        last_name="User",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF777",
        referred_by=None,
    )
    await user_repo.create(test_user)

    repo = DataPackageRepository(test_session)
    package = DataPackage(
        user_id=telegram_id,
        package_type=PackageType.BASIC,
        data_limit_bytes=10 * 1024**3,
        stars_paid=250,
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )
    saved = await repo.save(package, telegram_id)

    # Actualizar uso
    usage_bytes = 1024 * 1024 * 500  # 500 MB
    success = await repo.update_usage(saved.id, usage_bytes, telegram_id)
    assert success is True

    # Verificar
    updated = await repo.get_by_id(saved.id, telegram_id)
    assert updated.data_used_bytes == usage_bytes
