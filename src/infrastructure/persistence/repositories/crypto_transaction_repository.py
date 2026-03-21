"""Implementación de CryptoTransactionRepository con SQLAlchemy."""

from datetime import UTC
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.crypto_transaction import CryptoTransaction
from usipipo_commons.domain.enums.crypto_transaction_status import CryptoTransactionStatus

from src.core.domain.interfaces.i_crypto_transaction_repository import (
    ICryptoTransactionRepository,
)
from src.infrastructure.persistence.models.crypto_transaction_model import (
    CryptoTransactionModel,
)


class CryptoTransactionRepository(ICryptoTransactionRepository):
    """Implementación de repositorio de crypto transactions con SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, transaction: CryptoTransaction) -> CryptoTransaction:
        """Guarda una crypto transaction."""
        model = CryptoTransactionModel.from_entity(transaction)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_entity()

    async def get_by_id(self, transaction_id: UUID) -> CryptoTransaction | None:
        """Obtiene una transacción por ID."""
        result = await self.session.execute(
            select(CryptoTransactionModel).where(CryptoTransactionModel.id == transaction_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_tx_hash(self, tx_hash: str) -> CryptoTransaction | None:
        """Obtiene una transacción por hash."""
        result = await self.session.execute(
            select(CryptoTransactionModel).where(CryptoTransactionModel.tx_hash == tx_hash)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_wallet(self, wallet_address: str) -> list[CryptoTransaction]:
        """Obtiene transacciones por dirección de wallet."""
        result = await self.session.execute(
            select(CryptoTransactionModel)
            .where(CryptoTransactionModel.wallet_address == wallet_address)
            .order_by(CryptoTransactionModel.created_at.desc())
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def get_by_user_id(self, user_id: UUID, limit: int = 50) -> list[CryptoTransaction]:
        """Obtiene transacciones de un usuario."""
        result = await self.session.execute(
            select(CryptoTransactionModel)
            .where(CryptoTransactionModel.user_id == user_id)
            .order_by(CryptoTransactionModel.created_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def update_status(
        self, transaction_id: UUID, status: str, confirmations: int = 0
    ) -> bool:
        """Actualiza el estado de una transacción."""
        from datetime import datetime

        status_enum = CryptoTransactionStatus(status)

        update_values = {"status": status_enum, "confirmations": confirmations}

        if status == "confirmed":
            update_values["confirmed_at"] = datetime.now(UTC)

        result = await self.session.execute(
            update(CryptoTransactionModel)
            .where(CryptoTransactionModel.id == transaction_id)
            .values(**update_values)
        )
        await self.session.commit()
        return result.rowcount > 0 if result.rowcount else False
