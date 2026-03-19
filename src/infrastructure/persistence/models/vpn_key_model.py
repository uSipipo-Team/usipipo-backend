"""Modelo SQLAlchemy para claves VPN."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from usipipo_commons.domain.entities.vpn_key import VpnKey
from usipipo_commons.domain.enums.vpn_type import VpnType
from usipipo_commons.domain.enums.key_status import KeyStatus
from src.infrastructure.persistence.database import Base


class VpnKeyModel(Base):
    """Modelo SQLAlchemy para claves VPN."""

    __tablename__ = "vpn_keys"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    vpn_type: Mapped[VpnType] = mapped_column(
        SQLEnum(VpnType, name="vpn_type"), nullable=False
    )
    status: Mapped[KeyStatus] = mapped_column(
        SQLEnum(KeyStatus, name="key_status"), default=KeyStatus.ACTIVE
    )
    config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    data_used_gb: Mapped[float] = mapped_column(Float, default=0.0)
    data_limit_gb: Mapped[float] = mapped_column(Float, default=5.0)

    def to_entity(self) -> VpnKey:
        """
        Convierte modelo a entidad de dominio.

        Returns:
            VpnKey: Entidad de dominio
        """
        return VpnKey(
            id=self.id,
            user_id=self.user_id,
            name=self.name,
            vpn_type=self.vpn_type,
            status=self.status,
            config=self.config,
            created_at=self.created_at,
            expires_at=self.expires_at,
            last_used_at=self.last_used_at,
            data_used_gb=self.data_used_gb,
            data_limit_gb=self.data_limit_gb,
        )

    @classmethod
    def from_entity(cls, entity: VpnKey) -> "VpnKeyModel":
        """
        Crea modelo desde entidad.

        Args:
            entity: Entidad de dominio

        Returns:
            VpnKeyModel: Modelo SQLAlchemy
        """
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name,
            vpn_type=entity.vpn_type,
            status=entity.status,
            config=entity.config,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            last_used_at=entity.last_used_at,
            data_used_gb=entity.data_used_gb,
            data_limit_gb=entity.data_limit_gb,
        )
