"""Interface for subscription transaction repository."""

from abc import ABC, abstractmethod

from usipipo_commons.domain.entities.subscription_transaction import (
    SubscriptionTransaction,
)


class ISubscriptionTransactionRepository(ABC):
    """Contract for subscription transaction repository."""

    @abstractmethod
    async def save(self, transaction: SubscriptionTransaction) -> SubscriptionTransaction:
        """Save a subscription transaction."""
        pass

    @abstractmethod
    async def get_by_transaction_id(self, transaction_id: str) -> SubscriptionTransaction | None:
        """Get transaction by transaction ID."""
        pass

    @abstractmethod
    async def get_by_user(self, user_id: int, limit: int = 50) -> list[SubscriptionTransaction]:
        """Get transactions by user ID."""
        pass

    @abstractmethod
    async def mark_completed(self, transaction_id: str) -> bool:
        """Mark transaction as completed (prevent double-processing)."""
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Clean up expired pending transactions. Returns count of cleaned transactions."""
        pass
