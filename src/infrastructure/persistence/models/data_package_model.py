"""Modelo SQLAlchemy para paquetes de datos."""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from usipipo_commons.domain.entities.data_package import DataPackage, PackageType

from src.infrastructure.persistence.database import Base


class DataPackageModel(Base):
    """Modelo SQLAlchemy para paquetes de datos comprados."""

    __tablename__ = "data_packages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    package_type: Mapped[PackageType] = mapped_column(
        SQLEnum(PackageType, name="package_type"), nullable=False
    )
    data_limit_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    data_used_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    stars_paid: Mapped[int] = mapped_column(Integer, nullable=False)
    purchased_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    telegram_payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def to_entity(self) -> DataPackage:
        """
        Convierte modelo a entidad de dominio.

        Returns:
            DataPackage: Entidad de dominio
        """
        return DataPackage(
            id=self.id,
            user_id=self.user_id,
            package_type=self.package_type,
            data_limit_bytes=self.data_limit_bytes,
            data_used_bytes=self.data_used_bytes,
            stars_paid=self.stars_paid,
            purchased_at=self.purchased_at,
            expires_at=self.expires_at,
            is_active=self.is_active,
            telegram_payment_id=self.telegram_payment_id,
        )

    @classmethod
    def from_entity(cls, entity: DataPackage) -> "DataPackageModel":
        """
        Crea modelo desde entidad.

        Args:
            entity: Entidad de dominio

        Returns:
            DataPackageModel: Modelo SQLAlchemy
        """
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            package_type=entity.package_type,
            data_limit_bytes=entity.data_limit_bytes,
            data_used_bytes=entity.data_used_bytes,
            stars_paid=entity.stars_paid,
            purchased_at=entity.purchased_at,
            expires_at=entity.expires_at,
            is_active=entity.is_active,
            telegram_payment_id=entity.telegram_payment_id,
        )
