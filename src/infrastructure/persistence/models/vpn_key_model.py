"""Modelo SQLAlchemy para claves VPN."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from usipipo_commons.domain.entities.vpn_key import VpnKey
from usipipo_commons.domain.enums.key_type import KeyType

from src.infrastructure.persistence.database import Base


class VpnKeyModel(Base):
    """Modelo SQLAlchemy para claves VPN."""

    __tablename__ = "vpn_keys"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # telegram_id
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_type: Mapped[KeyType] = mapped_column(SQLEnum(KeyType, name="key_type"), nullable=False)
    key_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # config
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_bytes: Mapped[int] = mapped_column(Integer, default=0)
    data_limit_bytes: Mapped[int] = mapped_column(Integer, default=5 * 1024**3)
    billing_reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now
    )

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
            key_type=self.key_type,
            key_data=self.key_data,
            external_id=self.external_id,
            is_active=self.is_active,
            created_at=self.created_at,
            expires_at=self.expires_at,
            last_seen_at=self.last_seen_at,
            used_bytes=self.used_bytes,
            data_limit_bytes=self.data_limit_bytes,
            billing_reset_at=self.billing_reset_at,
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
            key_type=entity.key_type,
            key_data=entity.key_data,
            external_id=entity.external_id,
            is_active=entity.is_active,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            last_seen_at=entity.last_seen_at,
            used_bytes=entity.used_bytes,
            data_limit_bytes=entity.data_limit_bytes,
            billing_reset_at=entity.billing_reset_at,
        )
