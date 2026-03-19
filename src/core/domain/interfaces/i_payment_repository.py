"""Interface for payment repository."""

from abc import ABC, abstractmethod
from uuid import UUID

from usipipo_commons.domain.entities.payment import Payment


class IPaymentRepository(ABC):
    """Contract for payment repository."""

    @abstractmethod
    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        """Gets payment by ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[Payment]:
        """Gets all payments for a user."""
        pass

    @abstractmethod
    async def create(self, payment: Payment) -> Payment:
        """Creates a new payment."""
        pass

    @abstractmethod
    async def update(self, payment: Payment) -> Payment:
        """Updates an existing payment."""
        pass

    @abstractmethod
    async def delete(self, payment_id: UUID) -> bool:
        """Deletes a payment."""
        pass
