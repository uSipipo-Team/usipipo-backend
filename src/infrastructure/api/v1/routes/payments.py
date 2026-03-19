"""Payment routes."""

import logging
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.user import User

from src.core.application.services.payment_service import PaymentService
from src.infrastructure.api.v1.deps import get_current_user
from src.infrastructure.payment_gateways.telegram_stars_client import TelegramStarsClient
from src.infrastructure.payment_gateways.tron_dealer_client import TronDealerClient
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories.payment_repository import PaymentRepository
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.shared.schemas.payment import (
    CreateCryptoPaymentRequest,
    CreateTelegramStarsPaymentRequest,
    PaymentResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])


def get_tron_client() -> TronDealerClient:
    """Gets TronDealer client instance."""
    return TronDealerClient()


def get_telegram_stars_client() -> TelegramStarsClient:
    """Gets Telegram Stars client instance."""
    return TelegramStarsClient()


@router.post("/crypto", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_crypto_payment(
    request: CreateCryptoPaymentRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    tron_client: TronDealerClient = Depends(get_tron_client),
):
    """Creates a crypto payment (USDT)."""
    payment_repo = PaymentRepository(session)
    user_repo = UserRepository(session)
    payment_service = PaymentService(payment_repo, user_repo)

    try:
        invoice = await tron_client.create_invoice(
            amount_usd=request.amount_usd,
            network=request.network,
            external_id=str(current_user.id),
        )

        expires_at = datetime.utcnow() + timedelta(hours=1)

        payment = await payment_service.create_payment(
            user_id=current_user.id,
            amount_usd=request.amount_usd,
            gb_purchased=request.gb_purchased,
            method="crypto_usdt" if request.network == "BSC" else "crypto_trc20",
            crypto_address=invoice.get("address"),
            crypto_network=request.network,
            expires_at=expires_at,
        )
        return payment
    except ValueError as e:
        logger.error(f"Invalid payment request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create crypto payment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create payment: {e}")


@router.post("/stars", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_telegram_stars_payment(
    request: CreateTelegramStarsPaymentRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    telegram_client: TelegramStarsClient = Depends(get_telegram_stars_client),
):
    """Creates a Telegram Stars payment."""
    payment_repo = PaymentRepository(session)
    user_repo = UserRepository(session)
    payment_service = PaymentService(payment_repo, user_repo)

    try:
        invoice = await telegram_client.create_invoice(
            amount_usd=request.amount_usd,
            user_telegram_id=current_user.telegram_id,
        )

        expires_at = datetime.utcnow() + timedelta(minutes=15)

        payment = await payment_service.create_payment(
            user_id=current_user.id,
            amount_usd=request.amount_usd,
            gb_purchased=request.gb_purchased,
            method="telegram_stars",
            telegram_star_invoice_id=invoice.get("invoice_link"),
            expires_at=expires_at,
        )
        return payment
    except ValueError as e:
        logger.error(f"Invalid payment request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create Telegram Stars payment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create payment: {e}")


@router.get("/history", response_model=list[PaymentResponse])
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Gets payment history for the current user."""
    payment_repo = PaymentRepository(session)
    user_repo = UserRepository(session)
    payment_service = PaymentService(payment_repo, user_repo)

    payments = await payment_service.get_user_payments(current_user.id)
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Gets payment details by ID."""
    payment_repo = PaymentRepository(session)
    user_repo = UserRepository(session)
    payment_service = PaymentService(payment_repo, user_repo)

    payment = await payment_service.get_payment_by_id(payment_id)

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return payment
