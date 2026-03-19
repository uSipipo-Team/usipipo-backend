"""Telegram Stars payment gateway client."""

import logging
from typing import Any

import httpx

from src.shared.config import settings

logger = logging.getLogger(__name__)


class TelegramStarsClient:
    """Client for Telegram Stars payments."""

    def __init__(self):
        self.bot_token = settings.TELEGRAM_TOKEN
        self.base_url = "https://api.telegram.org"
        self.http = httpx.AsyncClient(base_url=self.base_url)

    async def create_invoice(
        self,
        amount_usd: float,
        user_telegram_id: int,
    ) -> dict[str, Any]:
        """Creates a Telegram Stars invoice."""
        try:
            stars_amount = int(amount_usd / 0.02)  # 1 Star ≈ $0.02

            response = await self.http.post(
                f"/bot{self.bot_token}/createInvoiceLink",
                json={
                    "title": "uSipipo VPN - GB Package",
                    "description": f"Purchase of {amount_usd} USD in VPN data",
                    "payload": f"user_{user_telegram_id}",
                    "provider_token": "",  # Empty for Telegram Stars
                    "currency": "XTR",  # Telegram Stars currency code
                    "prices": [{"label": "VPN Data", "amount": stars_amount}],
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create Telegram Stars invoice: {e}")
            raise

    async def answer_pre_checkout_query(
        self,
        query_id: str,
        ok: bool,
        error_message: str | None = None,
    ) -> bool:
        """Answers a pre-checkout query from Telegram."""
        try:
            payload = {
                "pre_checkout_query_id": query_id,
                "ok": ok,
            }
            if not ok and error_message:
                payload["error_message"] = error_message

            response = await self.http.post(
                f"/bot{self.bot_token}/answerPreCheckoutQuery",
                json=payload,
                timeout=10.0,
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to answer pre-checkout query: {e}")
            return False

    def verify_webhook_data(self, data: dict[str, Any]) -> bool:
        """Verifies pre-checkout query data from Telegram."""
        payload = data.get("invoice_payload", "")
        return payload.startswith("user_")

    async def close(self) -> None:
        """Closes the HTTP client."""
        await self.http.aclose()
