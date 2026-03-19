"""Webhooks de API v1."""

from .crypto import router as crypto_webhook_router
from .telegram_stars import router as telegram_stars_webhook_router

__all__ = ["crypto_webhook_router", "telegram_stars_webhook_router"]
