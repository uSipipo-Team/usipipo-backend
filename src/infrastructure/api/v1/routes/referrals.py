"""Endpoints para la gestión del sistema de referidos."""

from fastapi import APIRouter, Depends, HTTPException, status
from usipipo_commons.domain.entities.user import User

from src.core.application.services.referral_service import ReferralService
from src.infrastructure.api.v1.deps import get_current_user, get_referral_service
from src.shared.schemas.referral import (
    ReferralApplyRequest,
    ReferralOperationResponse,
    ReferralRedeemRequest,
    ReferralStatsResponse,
)

router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.get("/me", response_model=ReferralStatsResponse)
async def get_my_referral_stats(
    current_user: User = Depends(get_current_user),
    service: ReferralService = Depends(get_referral_service),
):
    """Obtiene las estadísticas de referidos del usuario actual."""
    try:
        stats = await service.get_referral_stats(current_user.id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/apply", response_model=ReferralOperationResponse)
async def apply_referral_code(
    request: ReferralApplyRequest,
    current_user: User = Depends(get_current_user),
    service: ReferralService = Depends(get_referral_service),
):
    """Aplica un código de referido al usuario actual."""
    result = await service.register_referral(
        new_user_id=current_user.id, referral_code=request.referral_code
    )

    if not result["success"]:
        error_msg = result.get("error", "Unknown error")
        if error_msg == "invalid_code":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Referral code not found"
            )
        if error_msg == "self_referral":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot refer yourself"
            )
        if error_msg == "already_referred":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="You already have a referrer"
            )

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg)

    return {"success": True, "message": "Referral code applied successfully", "data": result}


@router.post("/redeem", response_model=ReferralOperationResponse)
async def redeem_credits_for_data(
    request: ReferralRedeemRequest,
    current_user: User = Depends(get_current_user),
    service: ReferralService = Depends(get_referral_service),
):
    """Canjea créditos de referido por datos (GB)."""
    result = await service.redeem_credits_for_data(user_id=current_user.id, credits=request.credits)

    if not result["success"]:
        error_msg = result.get("error", "Unknown error")
        if error_msg == "insufficient_credits":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient referral credits"
            )
        if error_msg == "insufficient_credits_for_gb":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough credits to redeem at least 1GB (needs {result.get('required')} credits)",
            )

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg)

    return {
        "success": True,
        "message": f"Successfully redeemed {result['credits_spent']} credits for {result['gb_added']}GB",
        "data": result,
    }
