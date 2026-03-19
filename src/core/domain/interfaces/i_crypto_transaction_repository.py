"""Interface for crypto transaction repository."""

from abc import ABC, abstractmethod
from uuid import UUID

from usipipo_commons.domain.entities.crypto_transaction import CryptoTransaction, WebhookToken


class ICryptoTransactionRepository(ABC):
    """Contract for crypto transaction repository."""

    @abstractmethod
    async def save(self, transaction: CryptoTransaction) -> CryptoTransaction:
        """Saves a crypto transaction."""
        pass

    @abstractmethod
    async def get_by_id(self, transaction_id: UUID) -> CryptoTransaction | None:
        """Gets transaction by ID."""
        pass

    @abstractmethod
    async def get_by_tx_hash(self, tx_hash: str) -> CryptoTransaction | None:
        """Gets transaction by transaction hash."""
        pass

    @abstractmethod
    async def get_by_wallet(self, wallet_address: str) -> list[CryptoTransaction]:
        """Gets transactions by wallet address."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, limit: int = 50) -> list[CryptoTransaction]:
        """Gets transactions for a user."""
        pass

    @abstractmethod
    async def update_status(
        self, transaction_id: UUID, status: str, confirmations: int = 0
    ) -> bool:
        """Updates transaction status."""
        pass


class IWebhookTokenRepository(ABC):
    """Contract for webhook token repository."""

    @abstractmethod
    async def save(self, token: WebhookToken) -> WebhookToken:
        """Saves a webhook token."""
        pass

    @abstractmethod
    async def get_by_hash(self, token_hash: str) -> WebhookToken | None:
        """Gets token by hash."""
        pass

    @abstractmethod
    async def mark_used(self, token_id: UUID) -> bool:
        """Marks token as used."""
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Cleans up expired tokens. Returns count of cleaned tokens."""
        pass
