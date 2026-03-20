"""SQLAlchemy repository for subscription transactions."""

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.subscription_transaction import (
    SubscriptionTransaction,
)

from src.core.domain.interfaces.i_subscription_transaction_repository import (
    ISubscriptionTransactionRepository,
)
from src.infrastructure.persistence.models.subscription_transaction_model import (
    SubscriptionTransactionModel,
)


class SubscriptionTransactionRepository(ISubscriptionTransactionRepository):
    """SQLAlchemy implementation of ISubscriptionTransactionRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, transaction: SubscriptionTransaction) -> SubscriptionTransaction:
        """Save a subscription transaction."""
        model = SubscriptionTransactionModel.from_entity(transaction)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_entity()

    async def get_by_transaction_id(self, transaction_id: str) -> SubscriptionTransaction | None:
        """Get transaction by transaction ID."""
        result = await self.session.execute(
            select(SubscriptionTransactionModel).where(
                SubscriptionTransactionModel.transaction_id == transaction_id
            )
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_user(self, user_id: int, limit: int = 50) -> list[SubscriptionTransaction]:
        """Get transactions by user ID."""
        result = await self.session.execute(
            select(SubscriptionTransactionModel)
            .where(SubscriptionTransactionModel.user_id == user_id)
            .order_by(SubscriptionTransactionModel.created_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def mark_completed(self, transaction_id: str) -> bool:
        """Mark transaction as completed (prevent double-processing)."""
        result = await self.session.execute(
            select(SubscriptionTransactionModel).where(
                SubscriptionTransactionModel.transaction_id == transaction_id
            )
        )
        model = result.scalar_one_or_none()

        if not model:
            return False

        model.status = "completed"
        model.completed_at = datetime.now(UTC)
        await self.session.commit()
        return True

    async def cleanup_expired(self) -> int:
        """Clean up expired pending transactions. Returns count of cleaned transactions."""
        now = datetime.now(UTC)

        result = await self.session.execute(
            delete(SubscriptionTransactionModel).where(
                SubscriptionTransactionModel.status == "pending",
                SubscriptionTransactionModel.expires_at < now,
            )
        )
        await self.session.commit()
        return result.rowcount
