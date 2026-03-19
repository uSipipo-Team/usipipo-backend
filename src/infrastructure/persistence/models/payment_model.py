"""Modelo SQLAlchemy para pagos."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from usipipo_commons.domain.entities.payment import Payment
from usipipo_commons.domain.enums.payment_method import PaymentMethod
from usipipo_commons.domain.enums.payment_status import PaymentStatus

from src.infrastructure.persistence.database import Base


class PaymentModel(Base):
    """Modelo SQLAlchemy para pagos."""

    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    amount_usd: Mapped[float] = mapped_column(Float, nullable=False)
    gb_purchased: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(
        SQLEnum(PaymentMethod, name="payment_method"), nullable=False
    )
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus, name="payment_status"), default=PaymentStatus.PENDING
    )
    crypto_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    crypto_network: Mapped[str | None] = mapped_column(String(50), nullable=True)
    telegram_star_invoice_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    transaction_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def to_entity(self) -> Payment:
        """
        Converts model to domain entity.

        Returns:
            Payment: Domain entity
        """
        return Payment(
            id=self.id,
            user_id=self.user_id,
            amount_usd=self.amount_usd,
            gb_purchased=self.gb_purchased,
            method=self.method,
            status=self.status,
            crypto_address=self.crypto_address,
            crypto_network=self.crypto_network,
            telegram_star_invoice_id=self.telegram_star_invoice_id,
            created_at=self.created_at,
            expires_at=self.expires_at,
            paid_at=self.paid_at,
            transaction_hash=self.transaction_hash,
        )

    @classmethod
    def from_entity(cls, entity: Payment) -> "PaymentModel":
        """
        Creates model from entity.

        Args:
            entity: Domain entity

        Returns:
            PaymentModel: SQLAlchemy model
        """
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            amount_usd=entity.amount_usd,
            gb_purchased=entity.gb_purchased,
            method=entity.method,
            status=entity.status,
            crypto_address=entity.crypto_address,
            crypto_network=entity.crypto_network,
            telegram_star_invoice_id=entity.telegram_star_invoice_id,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            paid_at=entity.paid_at,
            transaction_hash=entity.transaction_hash,
        )
