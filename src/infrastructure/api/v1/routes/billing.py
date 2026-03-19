"""Billing routes."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.user import User

from src.core.application.services.billing_service import BillingService
from src.infrastructure.api.v1.deps import get_current_user
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.repositories.vpn_key_repository import VpnKeyRepository
from src.shared.schemas.billing import KeyUsageResponse, UsageResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Gets data usage for the current user."""
    try:
        user_repo = UserRepository(session)
        vpn_key_repo = VpnKeyRepository(session)
        billing_service = BillingService(user_repo, vpn_key_repo)

        usage = await billing_service.get_usage(current_user.id)
        return usage
    except Exception as e:
        logger.error(f"Failed to get usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage/{key_id}", response_model=KeyUsageResponse)
async def get_key_usage(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Gets data usage for a specific key."""
    try:
        user_repo = UserRepository(session)
        vpn_key_repo = VpnKeyRepository(session)
        billing_service = BillingService(user_repo, vpn_key_repo)

        usage = await billing_service.get_key_usage(current_user.id, key_id)
        return usage
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")
    except Exception as e:
        logger.error(f"Failed to get key usage: {e}")
        raise HTTPException(status_code=404, detail="Key not found")
