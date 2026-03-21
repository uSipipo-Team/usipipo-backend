"""Servicio de aplicación para gestión de suscripciones."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from usipipo_commons.domain.entities.subscription_plan import (
    PlanType,
    SubscriptionPlan,
)

from src.core.domain.interfaces.i_subscription_repository import (
    ISubscriptionRepository,
)
from src.core.domain.interfaces.i_user_repository import IUserRepository

logger = logging.getLogger(__name__)


@dataclass
class SubscriptionOption:
    """Opción de plan de suscripción."""

    name: str
    plan_type: PlanType
    duration_months: int
    stars: int
    usdt: float
    data_limit: str = "Unlimited"
    bonus_percent: int = 0


SUBSCRIPTION_OPTIONS: list[SubscriptionOption] = [
    SubscriptionOption(
        name="1 Month",
        plan_type=PlanType.ONE_MONTH,
        duration_months=1,
        stars=360,
        usdt=2.99,
    ),
    SubscriptionOption(
        name="3 Months",
        plan_type=PlanType.THREE_MONTHS,
        duration_months=3,
        stars=960,
        usdt=7.99,
        bonus_percent=11,  # ~10% discount
    ),
    SubscriptionOption(
        name="6 Months",
        plan_type=PlanType.SIX_MONTHS,
        duration_months=6,
        stars=1560,
        usdt=12.99,
        bonus_percent=13,  # ~15% discount
    ),
]


class SubscriptionService:
    """Servicio de aplicación para gestión de planes de suscripción."""

    def __init__(
        self,
        subscription_repo: ISubscriptionRepository,
        user_repo: IUserRepository,
    ):
        self.subscription_repo = subscription_repo
        self.user_repo = user_repo

    def get_available_plans(self) -> list[SubscriptionOption]:
        """
        Obtiene todos los planes de suscripción disponibles.

        Returns:
            Lista de opciones de planes disponibles
        """
        return SUBSCRIPTION_OPTIONS.copy()

    def get_plan_option(self, plan_type: str) -> SubscriptionOption | None:
        """
        Obtiene una opción de plan específica por tipo.

        Args:
            plan_type: Tipo de plan (one_month, three_months, six_months)

        Returns:
            Opción de plan o None si no existe
        """
        try:
            p_type = PlanType(plan_type.lower())
            for option in SUBSCRIPTION_OPTIONS:
                if option.plan_type == p_type:
                    return option
            return None
        except ValueError:
            return None

    async def is_premium_user(self, user_id: int, current_user_id: int) -> bool:
        """
        Verifica si un usuario tiene una suscripción activa.

        Args:
            user_id: ID de Telegram del usuario
            current_user_id: ID de Telegram del usuario actual (para permisos)

        Returns:
            True si tiene suscripción activa, False en caso contrario
        """
        active_plan = await self.subscription_repo.get_active_by_user(user_id, current_user_id)
        return active_plan is not None and not active_plan.is_expired

    async def get_user_subscription(
        self, user_id: int, current_user_id: int
    ) -> SubscriptionPlan | None:
        """
        Obtiene el plan de suscripción activo de un usuario.

        Args:
            user_id: ID de Telegram del usuario
            current_user_id: ID de Telegram del usuario actual (para permisos)

        Returns:
            Plan de suscripción o None si no tiene
        """
        return await self.subscription_repo.get_active_by_user(user_id, current_user_id)

    async def activate_subscription(
        self,
        user_id: int,
        plan_type: str,
        stars_paid: int,
        payment_id: str,
        current_user_id: int,
    ) -> SubscriptionPlan:
        """
        Activa una nueva suscripción para un usuario.

        Args:
            user_id: ID de Telegram del usuario
            plan_type: Tipo de plan a activar
            stars_paid: Cantidad de Stars pagados
            payment_id: ID del pago (para idempotencia)
            current_user_id: ID de Telegram del usuario actual (para permisos)

        Returns:
            Plan de suscripción activado

        Raises:
            ValueError: Si el usuario ya tiene una suscripción activa o el tipo de plan es inválido
        """
        # Verificar suscripción activa existente
        existing = await self.subscription_repo.get_active_by_user(user_id, current_user_id)
        if existing and not existing.is_expired:
            raise ValueError(f"User {user_id} already has an active subscription")

        # Verificar idempotencia (mismo payment_id)
        existing_by_payment = await self.subscription_repo.get_by_payment_id(
            payment_id, current_user_id
        )
        if existing_by_payment:
            logger.info(f"📦 Subscription already exists for payment {payment_id}")
            return existing_by_payment

        # Obtener opción de plan
        plan_option = self.get_plan_option(plan_type)
        if not plan_option:
            raise ValueError(f"Invalid plan type: {plan_type}")

        # Crear nueva suscripción
        now = datetime.now(UTC)
        expires = now + timedelta(days=plan_option.duration_months * 30)

        plan = SubscriptionPlan(
            user_id=user_id,
            plan_type=PlanType(plan_type.lower()),
            stars_paid=stars_paid,
            payment_id=payment_id,
            starts_at=now,
            expires_at=expires,
            is_active=True,
        )

        saved_plan = await self.subscription_repo.save(plan, current_user_id)
        logger.info(
            f"📦 Subscription activated for user {user_id}: {plan_option.name} ({stars_paid} stars)"
        )
        return saved_plan

    async def cancel_subscription(self, user_id: int, current_user_id: int) -> bool:
        """
        Cancela la suscripción activa de un usuario.

        Args:
            user_id: ID de Telegram del usuario
            current_user_id: ID de Telegram del usuario actual (para permisos)

        Returns:
            True si se canceló, False si no tenía suscripción activa
        """
        active_plan = await self.subscription_repo.get_active_by_user(user_id, current_user_id)
        if not active_plan:
            return False

        await self.subscription_repo.deactivate(active_plan.id, current_user_id)
        logger.info(f"📦 Subscription cancelled for user {user_id}")
        return True

    async def get_expiring_subscriptions(
        self, days: int = 3, current_user_id: int = 0
    ) -> list[SubscriptionPlan]:
        """
        Obtiene suscripciones que expiran en N días.

        Args:
            days: Días para considerar como "próximo a expirar"
            current_user_id: ID de Telegram del usuario actual (para permisos)

        Returns:
            Lista de planes que expiran pronto
        """
        return await self.subscription_repo.get_expiring_plans(days, current_user_id)

    async def get_expired_subscriptions(self, current_user_id: int = 0) -> list[SubscriptionPlan]:
        """
        Obtiene todas las suscripciones expiradas.

        Args:
            current_user_id: ID de Telegram del usuario actual (para permisos)

        Returns:
            Lista de planes expirados
        """
        return await self.subscription_repo.get_expired_plans(current_user_id)

    async def get_user_data_limit(self, user_id: int, current_user_id: int) -> int:
        """
        Obtiene el límite de datos del usuario basado en su estado de suscripción.

        Args:
            user_id: ID de Telegram del usuario
            current_user_id: ID de Telegram del usuario actual (para permisos)

        Returns:
            Límite de datos en bytes (-1 para ilimitado)
        """
        is_premium = await self.is_premium_user(user_id, current_user_id)
        if is_premium:
            return -1  # Datos ilimitados para usuarios premium

        # Usuarios no premium obtienen límite por defecto (10GB)
        # Nota: El campo free_data_limit_bytes no está en la entidad User actual
        return 10737418240  # 10GB en bytes
