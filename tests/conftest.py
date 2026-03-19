"""Configuración de fixtures para tests."""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from usipipo_commons.domain.entities.user import User

from src.infrastructure.persistence.database import Base, get_db, get_session
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.main import app
from src.shared import config
from src.shared.security.jwt import create_jwt_token

# Test database URL (SQLite en memoria para tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Override JWT_SECRET para tests (mínimo 32 bytes para evitar warnings)
config.settings.JWT_SECRET = "test-secret-key-must-be-at-least-32-bytes-long-for-security"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Configura el backend para anyio."""
    return "asyncio"


@pytest.fixture(scope="function")
async def test_engine():
    """Crea el engine de test."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession]:
    """Crea una sesión de test."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """Crea un cliente de test."""

    async def override_get_db():
        yield test_session

    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def auth_headers(client: AsyncClient, test_session: AsyncSession) -> dict:
    """Crea headers de autenticación para tests."""
    now = datetime.now(UTC)

    # Crear usuario de test
    test_user = User(
        id=uuid4(),
        telegram_id=123456,
        username="testuser",
        first_name="Test",
        last_name="User",
        is_admin=False,
        created_at=now,
        updated_at=now,
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="ref_test",
        referred_by=None,
    )

    user_repo = UserRepository(test_session)
    await user_repo.create(test_user)

    # Crear token JWT
    token = create_jwt_token(test_user.id, test_user.telegram_id)

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_auth_headers(client: AsyncClient, test_session: AsyncSession) -> dict:
    """Crea headers de autenticación para admin."""
    now = datetime.now(UTC)

    # Crear usuario admin de test
    test_admin = User(
        id=uuid4(),
        telegram_id=999999,
        username="adminuser",
        first_name="Admin",
        last_name="User",
        is_admin=True,
        created_at=now,
        updated_at=now,
        balance_gb=100.0,
        total_purchased_gb=50.0,
        referral_code="ref_admin",
        referred_by=None,
    )

    user_repo = UserRepository(test_session)
    await user_repo.create(test_admin)

    # Crear token JWT
    token = create_jwt_token(test_admin.id, test_admin.telegram_id)

    return {"Authorization": f"Bearer {token}"}
