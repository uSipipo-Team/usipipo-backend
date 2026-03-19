"""Implementación de CryptoOrderRepository con SQLAlchemy."""

from datetime import UTC
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.crypto_order import CryptoOrder
from usipipo_commons.domain.enums.crypto_order_status import CryptoOrderStatus

from src.core.domain.interfaces.i_crypto_order_repository import ICryptoOrderRepository
from src.infrastructure.persistence.models.crypto_order_model import CryptoOrderModel


class CryptoOrderRepository(ICryptoOrderRepository):
    """Implementación de repositorio de crypto orders con SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, order: CryptoOrder) -> CryptoOrder:
        """Guarda una crypto order."""
        model = CryptoOrderModel.from_entity(order)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_entity()

    async def get_by_id(self, order_id: UUID) -> CryptoOrder | None:
        """Obtiene una orden por ID."""
        result = await self.session.execute(
            select(CryptoOrderModel).where(CryptoOrderModel.id == order_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_wallet(self, wallet_address: str) -> CryptoOrder | None:
        """Obtiene una orden por dirección de wallet."""
        result = await self.session.execute(
            select(CryptoOrderModel)
            .where(CryptoOrderModel.wallet_address == wallet_address)
            .where(CryptoOrderModel.status == CryptoOrderStatus.PENDING)
            .order_by(CryptoOrderModel.created_at.desc())
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_user_id(self, user_id: UUID, limit: int = 50) -> list[CryptoOrder]:
        """Obtiene órdenes de un usuario."""
        result = await self.session.execute(
            select(CryptoOrderModel)
            .where(CryptoOrderModel.user_id == user_id)
            .order_by(CryptoOrderModel.created_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def mark_completed(self, order_id: UUID, tx_hash: str) -> bool:
        """Marca una orden como completada."""
        from datetime import datetime

        result = await self.session.execute(
            update(CryptoOrderModel)
            .where(CryptoOrderModel.id == order_id)
            .values(
                status=CryptoOrderStatus.COMPLETED,
                tx_hash=tx_hash,
                confirmed_at=datetime.now(UTC),
            )
        )
        await self.session.commit()
        return result.rowcount > 0

    async def mark_failed(self, order_id: UUID) -> bool:
        """Marca una orden como fallida."""
        result = await self.session.execute(
            update(CryptoOrderModel)
            .where(CryptoOrderModel.id == order_id)
            .values(status=CryptoOrderStatus.FAILED)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def mark_expired(self, order_id: UUID) -> bool:
        """Marca una orden como expirada."""
        result = await self.session.execute(
            update(CryptoOrderModel)
            .where(CryptoOrderModel.id == order_id)
            .values(status=CryptoOrderStatus.EXPIRED)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def cleanup_expired(self) -> int:
        """Limpia órdenes expiradas."""
        from datetime import datetime

        result = await self.session.execute(
            update(CryptoOrderModel)
            .where(CryptoOrderModel.status == CryptoOrderStatus.PENDING)
            .where(CryptoOrderModel.expires_at < datetime.now(UTC))
            .values(status=CryptoOrderStatus.EXPIRED)
        )
        await self.session.commit()
        return result.rowcount
