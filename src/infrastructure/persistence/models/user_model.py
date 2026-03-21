"""Modelo SQLAlchemy para usuarios."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from usipipo_commons.domain.entities.user import User

from src.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.ticket_model import TicketModel


class UserModel(Base):
    """Modelo SQLAlchemy para usuarios."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    balance_gb: Mapped[float] = mapped_column(Float, default=5.0)
    total_purchased_gb: Mapped[float] = mapped_column(Float, default=0.0)
    referral_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    referred_by: Mapped[UUID | None] = mapped_column(nullable=True, index=True)

    # Relationships
    tickets: Mapped[list["TicketModel"]] = relationship(
        back_populates="user", foreign_keys="TicketModel.user_id"
    )

    def to_entity(self) -> User:
        """
        Convierte modelo a entidad de dominio.

        Returns:
            User: Entidad de dominio
        """
        return User(
            id=self.id,
            telegram_id=self.telegram_id,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            is_admin=self.is_admin,
            created_at=self.created_at,
            updated_at=self.updated_at,
            balance_gb=self.balance_gb,
            total_purchased_gb=self.total_purchased_gb,
            referral_code=self.referral_code,
            referred_by=self.referred_by,
        )

    @classmethod
    def from_entity(cls, entity: User) -> "UserModel":
        """
        Crea modelo desde entidad.

        Args:
            entity: Entidad de dominio

        Returns:
            UserModel: Modelo SQLAlchemy
        """
        return cls(
            id=entity.id,
            telegram_id=entity.telegram_id,
            username=entity.username,
            first_name=entity.first_name,
            last_name=entity.last_name,
            is_admin=entity.is_admin,
            balance_gb=entity.balance_gb,
            total_purchased_gb=entity.total_purchased_gb,
            referral_code=entity.referral_code,
            referred_by=entity.referred_by,
        )
