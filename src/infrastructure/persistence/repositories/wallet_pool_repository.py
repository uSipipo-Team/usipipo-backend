"""Repositorio de pool de wallets con SQLAlchemy."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.wallet import WalletPool
from usipipo_commons.domain.enums.wallet_status import WalletStatus
from usipipo_commons.domain.interfaces.i_wallet_pool_repository import IWalletPoolRepository

from src.infrastructure.persistence.models.wallet_pool_model import WalletPoolModel


class WalletPoolRepository(IWalletPoolRepository):
    """Implementación de repositorio de pool de wallets con SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[WalletPool]:
        """
        Obtiene todas las entradas del pool.

        Returns:
            Lista de todas las entradas del pool
        """
        result = await self.session.execute(select(WalletPoolModel))
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def get_by_id(self, pool_id: UUID) -> WalletPool | None:
        """
        Obtiene entrada del pool por ID.

        Args:
            pool_id: UUID de la entrada

        Returns:
            WalletPool o None si no existe
        """
        result = await self.session.execute(
            select(WalletPoolModel).where(WalletPoolModel.id == pool_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_address(self, wallet_address: str) -> WalletPool | None:
        """
        Obtiene entrada del pool por dirección de wallet.

        Args:
            wallet_address: Dirección de la wallet

        Returns:
            WalletPool o None si no existe
        """
        result = await self.session.execute(
            select(WalletPoolModel).where(WalletPoolModel.wallet_address == wallet_address)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_available_wallets(self) -> list[WalletPool]:
        """
        Obtiene todas las wallets disponibles en el pool.

        Returns:
            Lista de wallets disponibles
        """
        from datetime import datetime

        result = await self.session.execute(
            select(WalletPoolModel)
            .where(WalletPoolModel.status == WalletStatus.AVAILABLE.value)
            .where(WalletPoolModel.expires_at > datetime.utcnow())
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def get_expired_wallets(self) -> list[WalletPool]:
        """
        Obtiene todas las wallets expiradas del pool.

        Returns:
            Lista de wallets expiradas
        """
        from datetime import datetime

        result = await self.session.execute(
            select(WalletPoolModel).where(WalletPoolModel.expires_at < datetime.utcnow())
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def create(self, pool_entry: WalletPool) -> WalletPool:
        """
        Crea una nueva entrada en el pool.

        Args:
            pool_entry: Entidad de WalletPool

        Returns:
            WalletPool creada
        """
        model = WalletPoolModel.from_entity(pool_entry)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return model.to_entity()

    async def update(self, pool_entry: WalletPool) -> WalletPool:
        """
        Actualiza entrada del pool existente.

        Args:
            pool_entry: Entidad de WalletPool actualizada

        Returns:
            WalletPool actualizada
        """
        model = await self.session.get(WalletPoolModel, pool_entry.id)
        if not model:
            raise ValueError(f"WalletPool {pool_entry.id} not found")

        model.status = pool_entry.status.value
        model.reused_by_user_id = pool_entry.reused_by_user_id
        model.reused_at = pool_entry.reused_at

        await self.session.flush()
        await self.session.refresh(model)
        return model.to_entity()

    async def delete(self, pool_id: UUID) -> bool:
        """
        Elimina entrada del pool.

        Args:
            pool_id: UUID de la entrada

        Returns:
            True si se eliminó, False si no existía
        """
        model = await self.session.get(WalletPoolModel, pool_id)
        if not model:
            return False

        await self.session.delete(model)
        await self.session.flush()
        return True

    async def get_reusable_for_user(self, user_id: UUID) -> WalletPool | None:
        """
        Obtiene wallet reutilizable de un usuario específico.

        Busca wallets expiradas que pertenecieron al usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            WalletPool o None
        """
        from datetime import datetime

        result = await self.session.execute(
            select(WalletPoolModel)
            .where(WalletPoolModel.original_user_id == user_id)
            .where(WalletPoolModel.status == WalletStatus.AVAILABLE.value)
            .where(WalletPoolModel.expires_at > datetime.utcnow())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_any_available(self) -> WalletPool | None:
        """
        Obtiene cualquier wallet disponible en el pool.

        Busca cualquier wallet expirada no en uso.

        Returns:
            WalletPool o None
        """
        from datetime import datetime

        result = await self.session.execute(
            select(WalletPoolModel)
            .where(WalletPoolModel.status == WalletStatus.AVAILABLE.value)
            .where(WalletPoolModel.expires_at > datetime.utcnow())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def cleanup_expired(self) -> int:
        """
        Limpia wallets expiradas del pool.

        Retorna la cantidad de entradas eliminadas.

        Returns:
            Cantidad de entradas eliminadas
        """
        from datetime import datetime

        result = await self.session.execute(
            delete(WalletPoolModel).where(WalletPoolModel.expires_at < datetime.utcnow())
        )
        await self.session.flush()
        return result.rowcount or 0  # type: ignore[attr-defined]
