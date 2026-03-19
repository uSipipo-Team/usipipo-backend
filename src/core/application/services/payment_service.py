"""Payment service for managing payments."""

from datetime import datetime
from uuid import UUID

from usipipo_commons.domain.entities.payment import Payment

from src.core.application.exceptions import (
    PaymentAlreadyCompletedError,
    PaymentExpiredError,
    PaymentNotFoundError,
    UserNotFoundError,
)
from src.core.domain.interfaces.i_payment_repository import IPaymentRepository
from src.core.domain.interfaces.i_user_repository import IUserRepository


class PaymentService:
    """Application service for payment management."""

    def __init__(
        self,
        payment_repo: IPaymentRepository,
        user_repo: IUserRepository,
    ):
        self.payment_repo = payment_repo
        self.user_repo = user_repo

    async def create_payment(
        self,
        user_id: UUID,
        amount_usd: float,
        gb_purchased: float,
        method: str,
        crypto_address: str | None = None,
        crypto_network: str | None = None,
        telegram_star_invoice_id: str | None = None,
        expires_at: datetime | None = None,
    ) -> Payment:
        """Creates a new payment."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        payment = Payment.create(
            user_id=user_id,
            amount_usd=amount_usd,
            gb_purchased=gb_purchased,
            method=method,
            crypto_address=crypto_address,
            crypto_network=crypto_network,
            telegram_star_invoice_id=telegram_star_invoice_id,
            expires_at=expires_at,
        )

        return await self.payment_repo.create(payment)

    async def complete_payment(
        self,
        payment_id: UUID,
        transaction_hash: str | None = None,
    ) -> Payment:
        """Completes a payment."""
        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment {payment_id} not found")

        if payment.status == "completed":
            raise PaymentAlreadyCompletedError(f"Payment {payment_id} already completed")

        if payment.status == "expired":
            raise PaymentExpiredError(f"Payment {payment_id} expired")

        payment.status = "completed"
        payment.paid_at = datetime.utcnow()
        payment.transaction_hash = transaction_hash

        updated_payment = await self.payment_repo.update(payment)

        user = await self.user_repo.get_by_id(payment.user_id)
        if user:
            user.balance_gb += payment.gb_purchased
            user.total_purchased_gb += payment.gb_purchased
            await self.user_repo.update(user)

        return updated_payment

    async def get_payment_by_id(self, payment_id: UUID) -> Payment | None:
        """Gets payment by ID."""
        return await self.payment_repo.get_by_id(payment_id)

    async def get_user_payments(self, user_id: UUID) -> list[Payment]:
        """Gets all payments for a user."""
        return await self.payment_repo.get_by_user_id(user_id)

    async def expire_payment(self, payment_id: UUID) -> Payment:
        """Expires a payment."""
        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment {payment_id} not found")

        payment.status = "expired"
        return await self.payment_repo.update(payment)
