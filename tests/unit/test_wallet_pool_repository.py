"""Tests unitarios para WalletPoolRepository."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.user import User
from usipipo_commons.domain.entities.wallet import WalletPool
from usipipo_commons.domain.enums.wallet_status import WalletStatus

from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.repositories.wallet_pool_repository import WalletPoolRepository


@pytest.mark.asyncio
async def test_create_wallet_pool(test_session: AsyncSession):
    """Test crear una entrada de pool de wallet."""
    user_repo = UserRepository(test_session)
    pool_repo = WalletPoolRepository(test_session)

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

    # Crear entrada de pool
    expires_at = datetime.now(UTC) + timedelta(hours=24)
    pool_entry = WalletPool.create(
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        original_user_id=user.id,
        expires_at=expires_at,
    )

    saved = await pool_repo.create(pool_entry)

    assert saved.id is not None
    assert saved.wallet_address == "0x1234567890abcdef1234567890abcdef12345678"
    assert saved.original_user_id == user.id
    assert saved.status == WalletStatus.AVAILABLE


@pytest.mark.asyncio
async def test_get_pool_by_id(test_session: AsyncSession):
    """Test obtener entrada de pool por ID."""
    user_repo = UserRepository(test_session)
    pool_repo = WalletPoolRepository(test_session)

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

    expires_at = datetime.now(UTC) + timedelta(hours=24)
    pool_entry = WalletPool.create(
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        original_user_id=user.id,
        expires_at=expires_at,
    )
    saved = await pool_repo.create(pool_entry)

    # Obtener por ID
    retrieved = await pool_repo.get_by_id(saved.id)

    assert retrieved is not None
    assert retrieved.id == saved.id
    assert retrieved.wallet_address == "0x1234567890abcdef1234567890abcdef12345678"


@pytest.mark.asyncio
async def test_get_pool_by_address(test_session: AsyncSession):
    """Test obtener entrada de pool por dirección."""
    user_repo = UserRepository(test_session)
    pool_repo = WalletPoolRepository(test_session)

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

    expires_at = datetime.now(UTC) + timedelta(hours=24)
    pool_entry = WalletPool.create(
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        original_user_id=user.id,
        expires_at=expires_at,
    )
    await pool_repo.create(pool_entry)

    # Obtener por address
    retrieved = await pool_repo.get_by_address("0x1234567890abcdef1234567890abcdef12345678")

    assert retrieved is not None
    assert retrieved.wallet_address == "0x1234567890abcdef1234567890abcdef12345678"


@pytest.mark.asyncio
async def test_get_available_wallets(test_session: AsyncSession):
    """Test obtener wallets disponibles."""
    user_repo = UserRepository(test_session)
    pool_repo = WalletPoolRepository(test_session)

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

    # Crear wallet disponible (no expirada)
    expires_at = datetime.now(UTC) + timedelta(hours=24)
    pool_entry = WalletPool.create(
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        original_user_id=user.id,
        expires_at=expires_at,
    )
    await pool_repo.create(pool_entry)

    # Obtener disponibles
    available = await pool_repo.get_available_wallets()

    assert len(available) >= 1
    assert any(w.wallet_address == "0x1234567890abcdef1234567890abcdef12345678" for w in available)


@pytest.mark.asyncio
async def test_get_expired_wallets(test_session: AsyncSession):
    """Test obtener wallets expiradas."""
    user_repo = UserRepository(test_session)
    pool_repo = WalletPoolRepository(test_session)

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

    # Crear wallet expirada
    expires_at = datetime.now(UTC) - timedelta(hours=1)
    pool_entry = WalletPool.create(
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        original_user_id=user.id,
        expires_at=expires_at,
    )
    await pool_repo.create(pool_entry)

    # Obtener expiradas
    expired = await pool_repo.get_expired_wallets()

    assert len(expired) >= 1
    assert any(w.wallet_address == "0x1234567890abcdef1234567890abcdef12345678" for w in expired)


@pytest.mark.asyncio
async def test_update_pool_entry(test_session: AsyncSession):
    """Test actualizar entrada de pool."""
    user_repo = UserRepository(test_session)
    pool_repo = WalletPoolRepository(test_session)

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

    expires_at = datetime.now(UTC) + timedelta(hours=24)
    pool_entry = WalletPool.create(
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        original_user_id=user.id,
        expires_at=expires_at,
    )
    saved = await pool_repo.create(pool_entry)

    # Marcar como reutilizada
    saved.mark_reused(user.id)
    updated = await pool_repo.update(saved)

    assert updated.status == WalletStatus.IN_USE
    assert updated.reused_by_user_id == user.id
    assert updated.reused_at is not None


@pytest.mark.asyncio
async def test_delete_pool_entry(test_session: AsyncSession):
    """Test eliminar entrada de pool."""
    user_repo = UserRepository(test_session)
    pool_repo = WalletPoolRepository(test_session)

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

    expires_at = datetime.now(UTC) + timedelta(hours=24)
    pool_entry = WalletPool.create(
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        original_user_id=user.id,
        expires_at=expires_at,
    )
    saved = await pool_repo.create(pool_entry)

    # Eliminar
    deleted = await pool_repo.delete(saved.id)
    assert deleted is True

    # Verificar que no existe
    retrieved = await pool_repo.get_by_id(saved.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_get_reusable_for_user(test_session: AsyncSession):
    """Test obtener wallet reutilizable para un usuario."""
    user_repo = UserRepository(test_session)
    pool_repo = WalletPoolRepository(test_session)

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

    # Crear wallet disponible para el usuario
    expires_at = datetime.now(UTC) + timedelta(hours=24)
    pool_entry = WalletPool.create(
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        original_user_id=user.id,
        expires_at=expires_at,
    )
    await pool_repo.create(pool_entry)

    # Obtener reutilizable para el usuario
    reusable = await pool_repo.get_reusable_for_user(user.id)

    assert reusable is not None
    assert reusable.original_user_id == user.id
    assert reusable.wallet_address == "0x1234567890abcdef1234567890abcdef12345678"


@pytest.mark.asyncio
async def test_cleanup_expired(test_session: AsyncSession):
    """Test limpiar wallets expiradas."""
    user_repo = UserRepository(test_session)
    pool_repo = WalletPoolRepository(test_session)

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

    # Crear wallet expirada
    expires_at = datetime.now(UTC) - timedelta(hours=1)
    pool_entry = WalletPool.create(
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        original_user_id=user.id,
        expires_at=expires_at,
    )
    await pool_repo.create(pool_entry)

    # Limpiar expiradas
    deleted_count = await pool_repo.cleanup_expired()

    assert deleted_count >= 1

    # Verificar que fue eliminada
    retrieved = await pool_repo.get_by_id(pool_entry.id)
    assert retrieved is None
