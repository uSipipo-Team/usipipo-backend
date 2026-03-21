"""Repositorio de paquetes de datos con SQLAlchemy."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.data_package import DataPackage

from src.core.domain.interfaces.i_data_package_repository import IDataPackageRepository
from src.infrastructure.persistence.models.data_package_model import DataPackageModel


class DataPackageRepository(IDataPackageRepository):
    """Implementación de repositorio de paquetes de datos con SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, data_package: DataPackage, current_user_id: int) -> DataPackage:
        """Guarda un nuevo paquete de datos o actualiza uno existente."""
        model = DataPackageModel.from_entity(data_package)
        model = await self.session.merge(model)
        await self.session.commit()
        return model.to_entity()

    async def get_by_id(self, package_id: uuid.UUID, current_user_id: int) -> DataPackage | None:
        """Busca un paquete específico por su ID."""
        result = await self.session.execute(
            select(DataPackageModel).where(DataPackageModel.id == package_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_user(self, telegram_id: int, current_user_id: int) -> list[DataPackage]:
        """Recupera todos los paquetes de un usuario."""
        result = await self.session.execute(
            select(DataPackageModel).where(DataPackageModel.user_id == telegram_id)
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def get_active_by_user(self, telegram_id: int, current_user_id: int) -> list[DataPackage]:
        """Recupera solo los paquetes activos de un usuario."""
        result = await self.session.execute(
            select(DataPackageModel).where(
                DataPackageModel.user_id == telegram_id, DataPackageModel.is_active
            )
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def get_valid_by_user(self, telegram_id: int, current_user_id: int) -> list[DataPackage]:
        """Recupera los paquetes activos y no expirados de un usuario."""
        now = datetime.now(UTC)
        result = await self.session.execute(
            select(DataPackageModel).where(
                DataPackageModel.user_id == telegram_id,
                DataPackageModel.is_active,
                DataPackageModel.expires_at > now,
            )
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def update_usage(
        self, package_id: uuid.UUID, bytes_used: int, current_user_id: int
    ) -> bool:
        """Actualiza el uso de datos de un paquete."""
        try:
            query = (
                update(DataPackageModel)
                .where(DataPackageModel.id == package_id)
                .values(data_used_bytes=DataPackageModel.data_used_bytes + bytes_used)
            )
            await self.session.execute(query)
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            return False

    async def deactivate(self, package_id: uuid.UUID, current_user_id: int) -> bool:
        """Desactiva un paquete."""
        try:
            query = (
                update(DataPackageModel)
                .where(DataPackageModel.id == package_id)
                .values(is_active=False)
            )
            await self.session.execute(query)
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            return False

    async def delete(self, package_id: uuid.UUID, current_user_id: int) -> bool:
        """Elimina un paquete de la base de datos."""
        try:
            query = delete(DataPackageModel).where(DataPackageModel.id == package_id)
            await self.session.execute(query)
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            return False

    async def get_expired_packages(self, current_user_id: int) -> list[DataPackage]:
        """Recupera todos los paquetes activos que han expirado."""
        now = datetime.now(UTC)
        result = await self.session.execute(
            select(DataPackageModel).where(
                DataPackageModel.is_active, DataPackageModel.expires_at <= now
            )
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def get_by_telegram_payment_id(
        self, telegram_payment_id: str, current_user_id: int
    ) -> DataPackage | None:
        """Busca un paquete por el ID de pago de Telegram."""
        result = await self.session.execute(
            select(DataPackageModel).where(
                DataPackageModel.telegram_payment_id == telegram_payment_id
            )
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_user_paginated(
        self, user_id: int, limit: int = 10, offset: int = 0, current_user_id: int = 0
    ) -> list[DataPackage]:
        """Get packages for a user with pagination."""
        result = await self.session.execute(
            select(DataPackageModel)
            .where(DataPackageModel.user_id == user_id)
            .order_by(DataPackageModel.purchased_at.desc())
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def count_by_user(self, user_id: int, current_user_id: int = 0) -> int:
        """Count total packages for a user."""
        result = await self.session.execute(
            select(func.count()).where(DataPackageModel.user_id == user_id)
        )
        return result.scalar() or 0
