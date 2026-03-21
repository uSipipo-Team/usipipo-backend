"""Modelo SQLAlchemy para wallets BSC."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from usipipo_commons.domain.entities.wallet import Wallet
from usipipo_commons.domain.enums.wallet_status import WalletStatus

from src.infrastructure.persistence.database import Base


class WalletModel(Base):
    """Modelo SQLAlchemy para wallet BSC de usuario."""

    __tablename__ = "wallets"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    address: Mapped[str] = mapped_column(String(42), unique=True, index=True, nullable=False)
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=WalletStatus.ACTIVE.value, index=True)
    balance_usdt: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_received_usdt: Mapped[float] = mapped_column(Float, default=0.0)
    transaction_count: Mapped[int] = mapped_column(default=0)

    # Relationship to user
    user: Mapped["UserModel"] = relationship(back_populates="wallet")

    def to_entity(self) -> Wallet:
        """
        Convierte modelo a entidad de dominio.

        Returns:
            Wallet: Entidad de dominio
        """
        return Wallet(
            id=self.id,
            user_id=self.user_id,
            address=self.address,
            label=self.label,
            status=WalletStatus(self.status),
            balance_usdt=self.balance_usdt,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_used_at=self.last_used_at,
            total_received_usdt=self.total_received_usdt,
            transaction_count=self.transaction_count,
        )

    @classmethod
    def from_entity(cls, entity: Wallet) -> "WalletModel":
        """
        Crea modelo desde entidad.

        Args:
            entity: Entidad de dominio

        Returns:
            WalletModel: Modelo SQLAlchemy
        """
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            address=entity.address,
            label=entity.label,
            status=entity.status.value,
            balance_usdt=entity.balance_usdt,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_used_at=entity.last_used_at,
            total_received_usdt=entity.total_received_usdt,
            transaction_count=entity.transaction_count,
        )
