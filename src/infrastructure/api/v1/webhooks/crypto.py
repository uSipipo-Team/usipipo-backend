"""Crypto payment webhook routes."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from src.core.application.services.notification_service import NotificationService
from src.core.application.services.payment_service import PaymentService
from src.infrastructure.payment_gateways.tron_dealer_client import TronDealerClient
from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


# Dependencies
def get_tron_client() -> TronDealerClient:
    """Gets TronDealer client instance."""
    return TronDealerClient()


@router.post("/crypto")
async def tron_dealer_webhook(
    request: Request,
    x_signature: str = Header(..., description="Webhook signature"),
    tron_client: TronDealerClient = Depends(get_tron_client),
):
    """
    Webhook from TronDealer for payment confirmation.

    TronDealer sends POST when a payment is confirmed.
    """
    payload = await request.body()

    if not tron_client.verify_webhook_signature(payload, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = await request.json()

    payment_id_str = data.get("external_id")
    transaction_hash = data.get("transaction_hash")
    amount_usd = data.get("amount")
    payment_status = data.get("status")

    if payment_status != "completed":
        return {"status": "ignored", "reason": f"Payment status: {payment_status}"}

    try:
        payment_id = UUID(payment_id_str)
    except (ValueError, TypeError):
        logger.error(f"Invalid payment_id in webhook: {payment_id_str}")
        return {"status": "error", "message": "Invalid payment_id"}

    try:
        from src.infrastructure.persistence.repositories.payment_repository import (
            PaymentRepository,
        )

        async for db in get_db():
            payment_repo = PaymentRepository(db)
            user_repo = UserRepository(db)
            payment_service = PaymentService(payment_repo, user_repo)
            notification_service = NotificationService(user_repo)

            await payment_service.complete_payment(
                payment_id=payment_id,
                transaction_hash=transaction_hash,
            )

            await notification_service.notify_payment_completed(
                user_id=payment_id,
                amount_usd=amount_usd,
                gb_purchased=data.get("gb_purchased", 0),
            )

            await notification_service.close()
            break

    except Exception as e:
        logger.error(f"Failed to complete payment {payment_id}: {e}")
        return {"status": "error", "message": str(e)}

    return {"status": "success"}
