"""SQLAlchemy model for subscription plans."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from usipipo_commons.domain.entities.subscription_plan import PlanType, SubscriptionPlan

from src.infrastructure.persistence.database import Base


class SubscriptionPlanModel(Base):
    """SQLAlchemy model for subscription plans."""

    __tablename__ = "subscription_plans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    plan_type: Mapped[PlanType] = mapped_column(SQLEnum(PlanType, name="plan_type"), nullable=False)
    stars_paid: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def to_entity(self) -> SubscriptionPlan:
        """Convert model to domain entity."""
        return SubscriptionPlan(
            id=self.id,
            user_id=self.user_id,
            plan_type=self.plan_type,
            stars_paid=self.stars_paid,
            payment_id=self.payment_id,
            starts_at=self.starts_at,
            expires_at=self.expires_at,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, entity: SubscriptionPlan) -> "SubscriptionPlanModel":
        """Create model from domain entity."""
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            plan_type=entity.plan_type,
            stars_paid=entity.stars_paid,
            payment_id=entity.payment_id,
            starts_at=entity.starts_at,
            expires_at=entity.expires_at,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
