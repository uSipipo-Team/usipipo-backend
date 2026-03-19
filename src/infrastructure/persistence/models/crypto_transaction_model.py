"""Modelo SQLAlchemy para crypto transactions."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from usipipo_commons.domain.entities.crypto_transaction import CryptoTransaction
from usipipo_commons.domain.enums.crypto_transaction_status import CryptoTransactionStatus

from src.infrastructure.persistence.database import Base


class CryptoTransactionModel(Base):
    """Modelo SQLAlchemy para crypto transactions."""

    __tablename__ = "crypto_transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    wallet_address: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    tx_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    token_symbol: Mapped[str] = mapped_column(String(20), default="USDT")
    status: Mapped[CryptoTransactionStatus] = mapped_column(
        SQLEnum(CryptoTransactionStatus, name="crypto_transaction_status"),
        default=CryptoTransactionStatus.PENDING,
    )
    confirmations: Mapped[int] = mapped_column(default=0)
    raw_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def to_entity(self) -> CryptoTransaction:
        """Convierte el modelo a entidad de dominio."""
        return CryptoTransaction(
            id=self.id,
            user_id=self.user_id,
            wallet_address=self.wallet_address,
            amount=self.amount,
            tx_hash=self.tx_hash,
            token_symbol=self.token_symbol,
            status=self.status,
            confirmations=self.confirmations,
            raw_payload=self.raw_payload,
            created_at=self.created_at,
            confirmed_at=self.confirmed_at,
        )

    @classmethod
    def from_entity(cls, entity: CryptoTransaction) -> "CryptoTransactionModel":
        """Crea el modelo desde una entidad."""
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            wallet_address=entity.wallet_address,
            amount=entity.amount,
            tx_hash=entity.tx_hash,
            token_symbol=entity.token_symbol,
            status=entity.status,
            confirmations=entity.confirmations,
            raw_payload=entity.raw_payload,
            created_at=entity.created_at,
            confirmed_at=entity.confirmed_at,
        )
