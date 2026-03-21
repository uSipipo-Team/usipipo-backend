"""SQLAlchemy model for subscription transactions."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from usipipo_commons.domain.entities.subscription_transaction import (
    SubscriptionTransaction,
    SubscriptionTransactionStatus,
)

from src.infrastructure.persistence.database import Base


class SubscriptionTransactionModel(Base):
    """SQLAlchemy model for subscription transactions."""

    __tablename__ = "subscription_transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    plan_type: Mapped[str] = mapped_column(nullable=False)
    amount_stars: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SubscriptionTransactionStatus] = mapped_column(
        SQLEnum(SubscriptionTransactionStatus, name="subscription_transaction_status"),
        nullable=False,
        default=SubscriptionTransactionStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def to_entity(self) -> SubscriptionTransaction:
        """Convert model to domain entity."""
        return SubscriptionTransaction(
            id=self.id,
            transaction_id=self.transaction_id,
            user_id=self.user_id,
            plan_type=self.plan_type,
            amount_stars=self.amount_stars,
            payload=self.payload,
            status=self.status,
            created_at=self.created_at,
            expires_at=self.expires_at,
            completed_at=self.completed_at,
        )

    @classmethod
    def from_entity(cls, entity: SubscriptionTransaction) -> "SubscriptionTransactionModel":
        """Create model from domain entity."""
        return cls(
            id=entity.id,
            transaction_id=entity.transaction_id,
            user_id=entity.user_id,
            plan_type=entity.plan_type,
            amount_stars=entity.amount_stars,
            payload=entity.payload,
            status=entity.status,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            completed_at=entity.completed_at,
        )
