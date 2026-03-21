"""Telegram Stars webhook routes."""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Request

from src.core.application.services.payment_service import PaymentService
from src.infrastructure.payment_gateways.telegram_stars_client import TelegramStarsClient
from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.repositories.payment_repository import PaymentRepository
from src.infrastructure.persistence.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


# Dependencies
def get_telegram_stars_client() -> TelegramStarsClient:
    """Gets Telegram Stars client instance."""
    return TelegramStarsClient()


@router.post("/telegram-stars")
async def telegram_stars_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    telegram_client: TelegramStarsClient = Depends(get_telegram_stars_client),
):
    """
    Webhook from Telegram for Telegram Stars payments.

    Telegram sends updates for pre_checkout_query and successful_payment.
    """
    data = await request.json()

    if "pre_checkout_query" in data:
        query = data["pre_checkout_query"]

        if not telegram_client.verify_webhook_data(query):
            await telegram_client.answer_pre_checkout_query(
                query_id=query["id"],
                ok=False,
                error_message="Invalid payment payload",
            )
            return {"status": "rejected"}

        await telegram_client.answer_pre_checkout_query(
            query_id=query["id"],
            ok=True,
        )

        return {"status": "ok"}

    if "message" in data and "successful_payment" in data["message"]:
        payment_data = data["message"]["successful_payment"]
        user_telegram_id = data["message"]["from"]["id"]
        total_amount = payment_data["total_amount"]

        payload = payment_data.get("invoice_payload", "")

        if not payload.startswith("user_"):
            logger.error(f"Invalid payload format: {payload}")
            return {"status": "error", "message": "Invalid payload"}

        background_tasks.add_task(
            process_telegram_stars_payment,
            user_telegram_id=user_telegram_id,
            amount_stars=total_amount,
        )

        return {"status": "ok"}

    return {"status": "ignored"}


async def process_telegram_stars_payment(
    user_telegram_id: int,
    amount_stars: int,
) -> None:
    """Processes a Telegram Stars payment in the background."""
    try:
        async for db in get_db():
            user_repo = UserRepository(db)
            payment_repo = PaymentRepository(db)
            payment_service = PaymentService(payment_repo, user_repo)

            user = await user_repo.get_by_telegram_id(user_telegram_id)
            if not user:
                logger.error(f"User not found: {user_telegram_id}")
                return

            payments = await payment_service.get_user_payments(user.id)
            pending_payments = [
                p for p in payments if p.status == "pending" and p.method == "telegram_stars"
            ]

            if pending_payments:
                payment = pending_payments[0]
                await payment_service.complete_payment(payment_id=payment.id)
                logger.info(f"Completed Telegram Stars payment: {payment.id}")
            else:
                logger.warning(f"No pending payment found for user {user_telegram_id}")
            break

    except Exception as e:
        logger.error(f"Failed to process Telegram Stars payment: {e}")
