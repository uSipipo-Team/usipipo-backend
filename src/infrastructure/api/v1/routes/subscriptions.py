"""Routes para gestión de suscripciones."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from usipipo_commons.domain.entities.user import User

from src.core.application.services.subscription_service import SubscriptionService
from src.infrastructure.api.v1.deps import get_current_user, get_subscription_service
from src.shared.schemas.subscription import (
    ActivateSubscriptionRequest,
    ActivateSubscriptionResponse,
    SubscriptionPlanResponse,
    UserSubscriptionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get(
    "/plans",
    response_model=list[SubscriptionPlanResponse],
    status_code=status.HTTP_200_OK,
)
async def list_subscription_plans(
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Lista todos los planes de suscripción disponibles.

    Este endpoint es público, no requiere autenticación.

    Args:
        subscription_service: Servicio de suscripciones

    Returns:
        list[SubscriptionPlanResponse]: Lista de planes disponibles
    """
    plans = subscription_service.get_available_plans()
    return [
        SubscriptionPlanResponse(
            name=plan.name,
            plan_type=plan.plan_type,
            duration_months=plan.duration_months,
            stars=plan.stars,
            usdt=plan.usdt,
            data_limit=plan.data_limit,
            bonus_percent=plan.bonus_percent,
        )
        for plan in plans
    ]


@router.post(
    "/activate",
    response_model=ActivateSubscriptionResponse,
    status_code=status.HTTP_200_OK,
)
async def activate_subscription(
    request: ActivateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Activa una nueva suscripción para el usuario autenticado.

    Requiere autenticación JWT.

    Args:
        request: Solicitud con tipo de plan y ID de pago
        current_user: Usuario autenticado
        subscription_service: Servicio de suscripciones

    Returns:
        ActivateSubscriptionResponse: Resultado de la activación

    Raises:
        HTTPException: 400 si hay error en la activación (usuario ya tiene suscripción activa o plan inválido)
    """
    try:
        subscription = await subscription_service.activate_subscription(
            user_id=current_user.telegram_id,
            plan_type=request.plan_type,
            stars_paid=0,  # Se obtiene del plan option internamente
            payment_id=request.payment_id,
            current_user_id=current_user.telegram_id,
        )

        return ActivateSubscriptionResponse(
            success=True,
            subscription_id=subscription.id,
            plan_type=subscription.plan_type,
            expires_at=subscription.expires_at,
            message=f"Subscription activated: {subscription.plan_type.value}",
        )
    except ValueError as e:
        logger.warning(f"Failed to activate subscription for user {current_user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error activating subscription for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate subscription: {str(e)}",
        )


@router.get(
    "/me",
    response_model=UserSubscriptionResponse | None,
    status_code=status.HTTP_200_OK,
)
async def get_user_subscription(
    current_user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Obtiene la suscripción actual del usuario autenticado.

    Requiere autenticación JWT.

    Args:
        current_user: Usuario autenticado
        subscription_service: Servicio de suscripciones

    Returns:
        UserSubscriptionResponse | None: Suscripción activa o None si no tiene
    """
    subscription = await subscription_service.get_user_subscription(
        user_id=current_user.telegram_id,
        current_user_id=current_user.telegram_id,
    )

    if not subscription:
        return None

    return UserSubscriptionResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        plan_type=subscription.plan_type,
        stars_paid=subscription.stars_paid,
        payment_id=subscription.payment_id,
        starts_at=subscription.starts_at,
        expires_at=subscription.expires_at,
        is_active=subscription.is_active,
        created_at=subscription.created_at,
        updated_at=subscription.updated_at,
        days_remaining=subscription.days_remaining,
        is_expiring_soon=subscription.is_expiring_soon,
        is_expired=subscription.is_expired,
    )
