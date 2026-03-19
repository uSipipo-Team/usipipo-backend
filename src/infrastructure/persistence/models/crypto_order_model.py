"""Modelo SQLAlchemy para crypto orders."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from usipipo_commons.domain.entities.crypto_order import CryptoOrder
from usipipo_commons.domain.enums.crypto_order_status import CryptoOrderStatus

from src.infrastructure.persistence.database import Base


class CryptoOrderModel(Base):
    """Modelo SQLAlchemy para crypto orders."""

    __tablename__ = "crypto_orders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    package_type: Mapped[str] = mapped_column(String(50), default="basic")
    amount_usdt: Mapped[float] = mapped_column(Float, nullable=False)
    wallet_address: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    tron_dealer_order_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[CryptoOrderStatus] = mapped_column(
        SQLEnum(CryptoOrderStatus, name="crypto_order_status"),
        default=CryptoOrderStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    tx_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def to_entity(self) -> CryptoOrder:
        """Convierte el modelo a entidad de dominio."""
        return CryptoOrder(
            id=self.id,
            user_id=self.user_id,
            package_type=self.package_type,
            amount_usdt=self.amount_usdt,
            wallet_address=self.wallet_address,
            tron_dealer_order_id=self.tron_dealer_order_id,
            status=self.status,
            created_at=self.created_at,
            expires_at=self.expires_at,
            tx_hash=self.tx_hash,
            confirmed_at=self.confirmed_at,
        )

    @classmethod
    def from_entity(cls, entity: CryptoOrder) -> "CryptoOrderModel":
        """Crea el modelo desde una entidad."""
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            package_type=entity.package_type,
            amount_usdt=entity.amount_usdt,
            wallet_address=entity.wallet_address,
            tron_dealer_order_id=entity.tron_dealer_order_id,
            status=entity.status,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            tx_hash=entity.tx_hash,
            confirmed_at=entity.confirmed_at,
        )
