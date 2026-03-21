"""Tests unitarios para WalletRepository."""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.user import User
from usipipo_commons.domain.entities.wallet import Wallet
from usipipo_commons.domain.enums.wallet_status import WalletStatus

from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.repositories.wallet_repository import WalletRepository


@pytest.mark.asyncio
async def test_create_wallet(test_session: AsyncSession):
    """Test crear una wallet."""
    user_repo = UserRepository(test_session)
    wallet_repo = WalletRepository(test_session)

    # Crear usuario
    user = User(
        id=uuid.uuid4(),
        telegram_id=123456,
        username="testuser",
        first_name="Test",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )
    await user_repo.create(user)

    # Crear wallet
    wallet = Wallet.create(
        user_id=user.id,
        address="0x1234567890abcdef1234567890abcdef12345678",
        label="test-wallet",
    )

    saved = await wallet_repo.create(wallet)

    assert saved.id is not None
    assert saved.user_id == user.id
    assert saved.address == "0x1234567890abcdef1234567890abcdef12345678"
    assert saved.status == WalletStatus.ACTIVE
    assert saved.balance_usdt == 0.0


@pytest.mark.asyncio
async def test_get_wallet_by_id(test_session: AsyncSession):
    """Test obtener wallet por ID."""
    user_repo = UserRepository(test_session)
    wallet_repo = WalletRepository(test_session)

    # Crear usuario y wallet
    user = User(
        id=uuid.uuid4(),
        telegram_id=123456,
        username="testuser",
        first_name="Test",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )
    await user_repo.create(user)

    wallet = Wallet.create(
        user_id=user.id,
        address="0x1234567890abcdef1234567890abcdef12345678",
        label="test-wallet",
    )
    saved = await wallet_repo.create(wallet)

    # Obtener por ID
    retrieved = await wallet_repo.get_by_id(saved.id)

    assert retrieved is not None
    assert retrieved.id == saved.id
    assert retrieved.user_id == user.id


@pytest.mark.asyncio
async def test_get_wallet_by_user_id(test_session: AsyncSession):
    """Test obtener wallet por user_id."""
    user_repo = UserRepository(test_session)
    wallet_repo = WalletRepository(test_session)

    user = User(
        id=uuid.uuid4(),
        telegram_id=123456,
        username="testuser",
        first_name="Test",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )
    await user_repo.create(user)

    wallet = Wallet.create(
        user_id=user.id,
        address="0x1234567890abcdef1234567890abcdef12345678",
        label="test-wallet",
    )
    await wallet_repo.create(wallet)

    # Obtener por user_id
    retrieved = await wallet_repo.get_by_user_id(user.id)

    assert retrieved is not None
    assert retrieved.user_id == user.id
    assert retrieved.address == "0x1234567890abcdef1234567890abcdef12345678"


@pytest.mark.asyncio
async def test_get_wallet_by_address(test_session: AsyncSession):
    """Test obtener wallet por dirección."""
    user_repo = UserRepository(test_session)
    wallet_repo = WalletRepository(test_session)

    user = User(
        id=uuid.uuid4(),
        telegram_id=123456,
        username="testuser",
        first_name="Test",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )
    await user_repo.create(user)

    wallet = Wallet.create(
        user_id=user.id,
        address="0x1234567890abcdef1234567890abcdef12345678",
        label="test-wallet",
    )
    await wallet_repo.create(wallet)

    # Obtener por address
    retrieved = await wallet_repo.get_by_address("0x1234567890abcdef1234567890abcdef12345678")

    assert retrieved is not None
    assert retrieved.address == "0x1234567890abcdef1234567890abcdef12345678"


@pytest.mark.asyncio
async def test_update_wallet(test_session: AsyncSession):
    """Test actualizar wallet."""
    user_repo = UserRepository(test_session)
    wallet_repo = WalletRepository(test_session)

    user = User(
        id=uuid.uuid4(),
        telegram_id=123456,
        username="testuser",
        first_name="Test",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )
    await user_repo.create(user)

    wallet = Wallet.create(
        user_id=user.id,
        address="0x1234567890abcdef1234567890abcdef12345678",
        label="test-wallet",
    )
    saved = await wallet_repo.create(wallet)

    # Actualizar
    saved.update_balance(100.0)
    updated = await wallet_repo.update(saved)

    assert updated.balance_usdt == 100.0
    assert updated.total_received_usdt == 100.0
    assert updated.transaction_count == 1


@pytest.mark.asyncio
async def test_delete_wallet(test_session: AsyncSession):
    """Test eliminar wallet."""
    user_repo = UserRepository(test_session)
    wallet_repo = WalletRepository(test_session)

    user = User(
        id=uuid.uuid4(),
        telegram_id=123456,
        username="testuser",
        first_name="Test",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )
    await user_repo.create(user)

    wallet = Wallet.create(
        user_id=user.id,
        address="0x1234567890abcdef1234567890abcdef12345678",
        label="test-wallet",
    )
    saved = await wallet_repo.create(wallet)

    # Eliminar
    deleted = await wallet_repo.delete(saved.id)
    assert deleted is True

    # Verificar que no existe
    retrieved = await wallet_repo.get_by_id(saved.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_get_active_wallets(test_session: AsyncSession):
    """Test obtener wallets activas."""
    user_repo = UserRepository(test_session)
    wallet_repo = WalletRepository(test_session)

    user = User(
        id=uuid.uuid4(),
        telegram_id=123456,
        username="testuser",
        first_name="Test",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )
    await user_repo.create(user)

    # Crear wallet activa
    wallet = Wallet.create(
        user_id=user.id,
        address="0x1234567890abcdef1234567890abcdef12345678",
        label="active-wallet",
    )
    await wallet_repo.create(wallet)

    # Obtener activas
    active = await wallet_repo.get_active_wallets()

    assert len(active) >= 1
    assert any(w.address == "0x1234567890abcdef1234567890abcdef12345678" for w in active)


@pytest.mark.asyncio
async def test_wallet_deactivate_activate(test_session: AsyncSession):
    """Test desactivar y activar wallet."""
    user_repo = UserRepository(test_session)
    wallet_repo = WalletRepository(test_session)

    user = User(
        id=uuid.uuid4(),
        telegram_id=123456,
        username="testuser",
        first_name="Test",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )
    await user_repo.create(user)

    wallet = Wallet.create(
        user_id=user.id,
        address="0x1234567890abcdef1234567890abcdef12345678",
        label="test-wallet",
    )
    await wallet_repo.create(wallet)

    # Desactivar
    wallet.deactivate()
    updated = await wallet_repo.update(wallet)
    assert updated.status == WalletStatus.INACTIVE

    # Activar
    wallet.activate()
    updated = await wallet_repo.update(wallet)
    assert updated.status == WalletStatus.ACTIVE
