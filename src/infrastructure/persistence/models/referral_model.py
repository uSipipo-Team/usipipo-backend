"""Modelo SQLAlchemy para referidos."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from usipipo_commons.domain.entities.referral import Referral

from src.infrastructure.persistence.database import Base


class ReferralModel(Base):
    """Modelo SQLAlchemy para relaciones de referidos."""

    __tablename__ = "referrals"

    id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    referrer_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    referred_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    bonus_applied: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relaciones
    referrer = relationship("UserModel", foreign_keys=[referrer_id])
    referred = relationship("UserModel", foreign_keys=[referred_id])

    def to_entity(self) -> Referral:
        """
        Convierte modelo a entidad de dominio.

        Returns:
            Referral: Entidad de dominio
        """
        return Referral(
            id=self.id,
            referrer_id=self.referrer_id,
            referred_id=self.referred_id,
            created_at=self.created_at,
            is_active=self.is_active,
            bonus_applied=self.bonus_applied,
        )

    @classmethod
    def from_entity(cls, entity: Referral) -> "ReferralModel":
        """
        Crea modelo desde entidad.

        Args:
            entity: Entidad de dominio

        Returns:
            ReferralModel: Modelo SQLAlchemy
        """
        return cls(
            id=entity.id,
            referrer_id=entity.referrer_id,
            referred_id=entity.referred_id,
            created_at=entity.created_at,
            is_active=entity.is_active,
            bonus_applied=entity.bonus_applied,
        )
