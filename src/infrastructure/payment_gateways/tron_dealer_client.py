"""TronDealer payment gateway client."""

import hashlib
import hmac
import logging
from typing import Any

import httpx

from src.shared.config import settings

logger = logging.getLogger(__name__)


class TronDealerClient:
    """Client for TronDealer API."""

    BASE_URL = "https://api.trondealer.com"

    def __init__(self):
        self.api_key = settings.TRON_DEALER_API_KEY
        self.webhook_secret = settings.TRON_DEALER_WEBHOOK_SECRET
        self.http = httpx.AsyncClient(base_url=self.BASE_URL)

    async def create_invoice(
        self,
        amount_usd: float,
        network: str,
        external_id: str,
    ) -> dict[str, Any]:
        """Creates an invoice in TronDealer."""
        try:
            response = await self.http.post(
                "/v1/invoice",
                json={
                    "amount": amount_usd,
                    "currency": "USD",
                    "network": network,
                    "external_id": external_id,
                },
                headers={"X-API-Key": self.api_key},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create TronDealer invoice: {e}")
            raise

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verifies webhook signature."""
        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload,
                hashlib.sha256,
            ).hexdigest()

            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Failed to verify webhook signature: {e}")
            return False

    async def close(self) -> None:
        """Closes the HTTP client."""
        await self.http.aclose()
