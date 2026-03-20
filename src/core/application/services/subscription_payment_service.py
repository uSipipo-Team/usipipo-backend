"""Subscription payment service for orchestrating subscription payments (Stars + Crypto)."""

import logging
from typing import TYPE_CHECKING, Any, Optional

from src.infrastructure.payment_gateways.telegram_stars_client import TelegramStarsClient
from src.shared.config import settings

if TYPE_CHECKING:
    from src.core.application.services.crypto_payment_service import CryptoPaymentService
    from src.core.application.services.subscription_service import (
        SubscriptionOption,
        SubscriptionService,
    )

logger = logging.getLogger(__name__)


class SubscriptionPaymentService:
    """Orchestrates subscription payments via Telegram Stars and Crypto."""

    def __init__(
        self,
        subscription_service: "SubscriptionService",
        crypto_payment_service: Optional["CryptoPaymentService"] = None,
        telegram_stars_client: TelegramStarsClient | None = None,
    ):
        """
        Initialize the subscription payment service.

        Args:
            subscription_service: Service for managing subscriptions
            crypto_payment_service: Optional service for crypto payments
            telegram_stars_client: Optional client for Telegram Stars invoices
        """
        self.subscription_service = subscription_service
        self.crypto_payment_service = crypto_payment_service
        self.telegram_stars_client = telegram_stars_client or TelegramStarsClient()

    async def create_stars_invoice(
        self,
        user_id: int,
        plan_type: str,
        transaction_id: str,
    ) -> dict[str, Any]:
        """
        Create a Telegram Stars invoice for a subscription.

        Args:
            user_id: Telegram user ID
            plan_type: Type of plan (one_month, three_months, six_months)
            transaction_id: Unique transaction identifier

        Returns:
            dict with success status and invoice details

        Raises:
            ValueError: If plan is invalid or user already has subscription
            Exception: If invoice creation fails
        """
        plan_option = self.subscription_service.get_plan_option(plan_type)

        if not plan_option:
            raise ValueError(f"Plan no válido: {plan_type}")

        # Check existing subscription
        is_premium = await self.subscription_service.is_premium_user(user_id, user_id)
        if is_premium:
            raise ValueError("Ya tienes una suscripción activa")

        # Create invoice payload
        payload = f"subscription_{plan_type}_{user_id}_{transaction_id}"

        # Send invoice via Telegram Stars client
        invoice_result = await self._send_stars_invoice(
            user_id=user_id,
            plan_option=plan_option,
            payload=payload,
        )

        if not invoice_result.get("success"):
            raise Exception("No se pudo crear la factura")

        logger.info(
            f"⭐ Stars invoice created for subscription: "
            f"user {user_id}, plan {plan_type}, {plan_option.stars} stars"
        )

        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount_stars": plan_option.stars,
            "payload": payload,
            "invoice_link": invoice_result.get("invoice_link"),
        }

    async def _send_stars_invoice(
        self,
        user_id: int,
        plan_option: "SubscriptionOption",
        payload: str,
    ) -> dict[str, Any]:
        """
        Send Telegram Stars invoice to user.

        Args:
            user_id: Telegram user ID
            plan_option: Subscription plan option
            payload: Invoice payload

        Returns:
            dict with invoice result
        """
        try:
            # Convert USDT to Stars using the client
            invoice_result = await self.telegram_stars_client.create_invoice(
                amount_usd=plan_option.usdt,
                user_telegram_id=user_id,
            )

            logger.info(
                f"⭐ Stars invoice sent to user {user_id}: {plan_option.name} ({plan_option.stars} XTR)"
            )
            return {"success": True, "invoice_link": invoice_result.get("result", {})}

        except Exception as e:
            logger.error(f"Error sending stars invoice to user {user_id}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def create_crypto_order(
        self,
        user_id: int,
        plan_type: str,
        transaction_id: str,
    ) -> dict[str, Any]:
        """
        Create a crypto payment order for a subscription.

        Args:
            user_id: Telegram user ID
            plan_type: Type of plan (one_month, three_months, six_months)
            transaction_id: Unique transaction identifier

        Returns:
            dict with order details and payment instructions

        Raises:
            ValueError: If plan is invalid or user already has subscription
        """
        plan_option = self.subscription_service.get_plan_option(plan_type)

        if not plan_option:
            raise ValueError(f"Plan no válido: {plan_type}")

        # Check existing subscription
        is_premium = await self.subscription_service.is_premium_user(user_id, user_id)
        if is_premium:
            raise ValueError("Ya tienes una suscripción activa")

        # Calculate USDT amount
        usdt_amount = plan_option.usdt

        # Generate wallet address and QR code URL
        # For now, use a placeholder - in production this would come from a payment gateway
        wallet_address = (
            settings.TRON_DEALER_WALLET_ADDRESS
            if hasattr(settings, "TRON_DEALER_WALLET_ADDRESS")
            and settings.TRON_DEALER_WALLET_ADDRESS
            else "0x..."
        )
        qr_code_url = f"/api/v1/crypto/qr/{transaction_id}"

        logger.info(
            f"💰 Crypto order created for subscription: "
            f"user {user_id}, plan {plan_type}, {usdt_amount} USDT"
        )

        return {
            "success": True,
            "transaction_id": transaction_id,
            "plan_type": plan_type,
            "amount_usdt": usdt_amount,
            "wallet_address": wallet_address,
            "qr_code_url": qr_code_url,
        }

    async def handle_stars_payment_success(
        self,
        user_id: int,
        plan_type: str,
        transaction_id: str,
        telegram_payment_id: str,
        current_user_id: int,
    ) -> dict[str, Any]:
        """
        Handle successful Telegram Stars payment.

        Args:
            user_id: Telegram user ID
            plan_type: Type of plan
            transaction_id: Original transaction identifier
            telegram_payment_id: Telegram payment ID from webhook
            current_user_id: Current user ID for permissions

        Returns:
            dict with activation result
        """
        plan_option = self.subscription_service.get_plan_option(plan_type)

        if not plan_option:
            raise ValueError(f"Plan no válido: {plan_type}")

        # Activate subscription
        subscription = await self.subscription_service.activate_subscription(
            user_id=user_id,
            plan_type=plan_type,
            stars_paid=plan_option.stars,
            payment_id=telegram_payment_id,
            current_user_id=current_user_id,
        )

        logger.info(
            f"⭐ Stars payment successful for subscription: "
            f"user {user_id}, plan {plan_type}, payment {telegram_payment_id}"
        )

        return {
            "success": True,
            "subscription_id": str(subscription.id),
            "plan_type": plan_type,
            "expires_at": subscription.expires_at.isoformat(),
        }

    async def handle_crypto_payment_success(
        self,
        user_id: int,
        plan_type: str,
        transaction_id: str,
        crypto_payment_id: str,
        current_user_id: int,
    ) -> dict[str, Any]:
        """
        Handle successful crypto payment.

        Args:
            user_id: Telegram user ID
            plan_type: Type of plan
            transaction_id: Original transaction identifier
            crypto_payment_id: Crypto payment/transaction ID
            current_user_id: Current user ID for permissions

        Returns:
            dict with activation result
        """
        plan_option = self.subscription_service.get_plan_option(plan_type)

        if not plan_option:
            raise ValueError(f"Plan no válido: {plan_type}")

        # Activate subscription
        subscription = await self.subscription_service.activate_subscription(
            user_id=user_id,
            plan_type=plan_type,
            stars_paid=plan_option.stars,
            payment_id=crypto_payment_id,
            current_user_id=current_user_id,
        )

        logger.info(
            f"💰 Crypto payment successful for subscription: "
            f"user {user_id}, plan {plan_type}, payment {crypto_payment_id}"
        )

        return {
            "success": True,
            "subscription_id": str(subscription.id),
            "plan_type": plan_type,
            "expires_at": subscription.expires_at.isoformat(),
        }
