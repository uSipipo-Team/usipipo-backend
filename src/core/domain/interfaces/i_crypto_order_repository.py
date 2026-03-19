"""Interface for crypto order repository."""

from abc import ABC, abstractmethod
from uuid import UUID

from usipipo_commons.domain.entities.crypto_order import CryptoOrder


class ICryptoOrderRepository(ABC):
    """Contract for crypto order repository."""

    @abstractmethod
    async def save(self, order: CryptoOrder) -> CryptoOrder:
        """Saves a crypto order."""
        pass

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> CryptoOrder | None:
        """Gets order by ID."""
        pass

    @abstractmethod
    async def get_by_wallet(self, wallet_address: str) -> CryptoOrder | None:
        """Gets order by wallet address."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, limit: int = 50) -> list[CryptoOrder]:
        """Gets orders for a user."""
        pass

    @abstractmethod
    async def mark_completed(self, order_id: UUID, tx_hash: str) -> bool:
        """Marks order as completed."""
        pass

    @abstractmethod
    async def mark_failed(self, order_id: UUID) -> bool:
        """Marks order as failed."""
        pass

    @abstractmethod
    async def mark_expired(self, order_id: UUID) -> bool:
        """Marks order as expired."""
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Cleans up expired orders. Returns count of cleaned orders."""
        pass
