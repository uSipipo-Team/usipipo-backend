"""Modelo SQLAlchemy para ciclos de facturación por consumo."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from usipipo_commons.domain.entities.consumption_billing import ConsumptionBilling
from usipipo_commons.domain.enums.billing_status import BillingStatus

from src.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.consumption_invoice_model import (
        ConsumptionInvoiceModel,
    )


class ConsumptionBillingModel(Base):
    """Modelo SQLAlchemy para ciclos de facturación por consumo."""

    __tablename__ = "consumption_billings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,  # Un ciclo activo por usuario
    )
    status: Mapped[str] = mapped_column(
        SQLEnum("active", "closed", "paid", name="billing_status_enum"),
        nullable=False,
        default="active",
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    mb_consumed: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.00")
    )
    total_cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.00")
    )
    price_per_mb_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 12), nullable=False, default=Decimal("0.000244140625")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # Relationships
    invoices: Mapped[list["ConsumptionInvoiceModel"]] = relationship(
        back_populates="billing",
        cascade="all, delete-orphan",
        foreign_keys="ConsumptionInvoiceModel.billing_id",
    )

    @classmethod
    def from_entity(cls, entity: ConsumptionBilling) -> "ConsumptionBillingModel":
        """Convierte una entidad de dominio a modelo SQLAlchemy."""
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            status=entity.status.value,
            started_at=entity.started_at,
            ended_at=entity.ended_at,
            mb_consumed=entity.mb_consumed,
            total_cost_usd=entity.total_cost_usd,
            price_per_mb_usd=entity.price_per_mb_usd,
            created_at=entity.created_at,
        )

    def to_entity(self) -> ConsumptionBilling:
        """Convierte el modelo SQLAlchemy a entidad de dominio."""
        return ConsumptionBilling(
            id=self.id,
            user_id=self.user_id,
            status=BillingStatus(self.status),
            started_at=self.started_at,
            ended_at=self.ended_at,
            mb_consumed=self.mb_consumed,
            total_cost_usd=self.total_cost_usd,
            price_per_mb_usd=self.price_per_mb_usd,
            created_at=self.created_at,
        )

    def __repr__(self) -> str:
        return (
            f"<ConsumptionBillingModel(id={self.id}, user_id={self.user_id}, "
            f"status={self.status}, mb_consumed={self.mb_consumed})>"
        )
