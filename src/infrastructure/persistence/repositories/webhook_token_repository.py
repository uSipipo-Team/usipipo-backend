"""Implementación de WebhookTokenRepository con SQLAlchemy."""

from datetime import UTC
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.crypto_transaction import WebhookToken

from src.core.domain.interfaces.i_crypto_transaction_repository import (
    IWebhookTokenRepository,
)
from src.infrastructure.persistence.models.webhook_token_model import (
    WebhookTokenModel,
)


class WebhookTokenRepository(IWebhookTokenRepository):
    """Implementación de repositorio de webhook tokens con SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, token: WebhookToken) -> WebhookToken:
        """Guarda un webhook token."""
        model = WebhookTokenModel.from_entity(token)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_entity()

    async def get_by_hash(self, token_hash: str) -> WebhookToken | None:
        """Obtiene un token por hash."""
        result = await self.session.execute(
            select(WebhookTokenModel).where(WebhookTokenModel.token_hash == token_hash)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def mark_used(self, token_id: UUID) -> bool:
        """Marca un token como usado."""
        from datetime import datetime

        result = await self.session.execute(
            update(WebhookTokenModel)
            .where(WebhookTokenModel.id == token_id)
            .values(used_at=datetime.now(UTC))
        )
        await self.session.commit()
        rowcount = result.rowcount or 0
        return rowcount > 0

    async def cleanup_expired(self) -> int:
        """Limpia tokens expirados."""
        from datetime import datetime

        result = await self.session.execute(
            update(WebhookTokenModel)
            .where(WebhookTokenModel.expires_at < datetime.now(UTC))
            .where(WebhookTokenModel.used_at.is_(None))
        )
        await self.session.commit()
        return result.rowcount or 0
