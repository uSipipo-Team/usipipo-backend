"""Modelo SQLAlchemy para webhook tokens."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from usipipo_commons.domain.entities.crypto_transaction import WebhookToken

from src.infrastructure.persistence.database import Base


class WebhookTokenModel(Base):
    """Modelo SQLAlchemy para webhook tokens."""

    __tablename__ = "webhook_tokens"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    purpose: Mapped[str] = mapped_column(String(50), default="tron_dealer")
    extra_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def to_entity(self) -> WebhookToken:
        """Convierte el modelo a entidad de dominio."""
        import json

        extra = json.loads(self.extra_data) if self.extra_data else {}

        return WebhookToken(
            id=self.id,
            token_hash=self.token_hash,
            purpose=self.purpose,
            extra_data=extra,
            created_at=self.created_at,
            expires_at=self.expires_at,
            used_at=self.used_at,
        )

    @classmethod
    def from_entity(cls, entity: WebhookToken) -> "WebhookTokenModel":
        """Crea el modelo desde una entidad."""
        import json

        return cls(
            id=entity.id,
            token_hash=entity.token_hash,
            purpose=entity.purpose,
            extra_data=json.dumps(entity.extra_data) if entity.extra_data else None,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            used_at=entity.used_at,
        )
