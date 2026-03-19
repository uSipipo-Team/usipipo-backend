"""Notification service for sending push notifications to users via Telegram."""

import logging
from uuid import UUID

import httpx

from src.core.domain.interfaces.i_user_repository import IUserRepository
from src.shared.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending push notifications to users via Telegram."""

    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo
        self.bot_token = settings.TELEGRAM_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.http = httpx.AsyncClient(base_url=self.base_url)

    async def notify_user(self, telegram_id: int, message: str) -> bool:
        """Sends a message to a user via Telegram."""
        try:
            response = await self.http.post(
                "/sendMessage",
                json={
                    "chat_id": telegram_id,
                    "text": message,
                    "parse_mode": "HTML",
                },
                timeout=10.0,
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send notification to {telegram_id}: {e}")
            return False

    async def notify_payment_completed(
        self, user_id: UUID, amount_usd: float, gb_purchased: float
    ) -> None:
        """Notifies user that their payment was completed."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return

        message = (
            f"✅ <b>Pago Completado</b>\n\n"
            f"Monto: ${amount_usd} USD\n"
            f"GB agregados: {gb_purchased} GB\n\n"
            f"Tu nuevo saldo: {user.balance_gb + gb_purchased} GB"
        )

        await self.notify_user(user.telegram_id, message)

    async def notify_key_expiring_soon(self, user_id: UUID, key_name: str, days_left: int) -> None:
        """Notifies user that a key is about to expire."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return

        message = (
            f"⚠️ <b>Clave por Expirar</b>\n\n"
            f"Clave: {key_name}\n"
            f"Días restantes: {days_left}\n\n"
            f"Renueva desde el bot o la Mini App."
        )

        await self.notify_user(user.telegram_id, message)

    async def close(self) -> None:
        """Closes the HTTP client."""
        await self.http.aclose()
