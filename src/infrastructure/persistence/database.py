"""Configuración de base de datos SQLAlchemy."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.shared.config import settings


class Base(DeclarativeBase):
    """Clase base para modelos SQLAlchemy."""

    pass


# Crear engine asíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """
    Dependency para obtener sesión de base de datos (synchronous).

    Returns:
        AsyncSession: Sesión asíncrona de SQLAlchemy
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession]:
    """
    Dependency para obtener sesión de base de datos.

    Yields:
        AsyncSession: Sesión asíncrona de SQLAlchemy
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Inicializa la base de datos (crear tablas)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Cierra la conexión a la base de datos."""
    await engine.dispose()
