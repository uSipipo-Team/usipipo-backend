"""Modelo SQLAlchemy para pool de wallets reutilizables."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from usipipo_commons.domain.entities.wallet import WalletPool
from usipipo_commons.domain.enums.wallet_status import WalletStatus

from src.infrastructure.persistence.database import Base


class WalletPoolModel(Base):
    """Modelo SQLAlchemy para entrada de pool de wallet."""

    __tablename__ = "wallet_pools"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    wallet_address: Mapped[str] = mapped_column(String(42), unique=True, index=True, nullable=False)
    original_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default=WalletStatus.AVAILABLE.value, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    released_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reused_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    reused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def to_entity(self) -> WalletPool:
        """
        Convierte modelo a entidad de dominio.

        Returns:
            WalletPool: Entidad de dominio
        """
        return WalletPool(
            id=self.id,
            wallet_address=self.wallet_address,
            original_user_id=self.original_user_id,
            status=WalletStatus(self.status),
            created_at=self.created_at,
            released_at=self.released_at,
            expires_at=self.expires_at,
            reused_by_user_id=self.reused_by_user_id,
            reused_at=self.reused_at,
        )

    @classmethod
    def from_entity(cls, entity: WalletPool) -> "WalletPoolModel":
        """
        Crea modelo desde entidad.

        Args:
            entity: Entidad de dominio

        Returns:
            WalletPoolModel: Modelo SQLAlchemy
        """
        return cls(
            id=entity.id,
            wallet_address=entity.wallet_address,
            original_user_id=entity.original_user_id,
            status=entity.status.value,
            created_at=entity.created_at,
            released_at=entity.released_at,
            expires_at=entity.expires_at,
            reused_by_user_id=entity.reused_by_user_id,
            reused_at=entity.reused_at,
        )
