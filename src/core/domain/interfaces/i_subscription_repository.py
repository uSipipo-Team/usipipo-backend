"""Repository interface for subscription operations."""

from abc import ABC, abstractmethod
from uuid import UUID

from usipipo_commons.domain.entities.subscription_plan import SubscriptionPlan


class ISubscriptionRepository(ABC):
    """Contrato para repositorio de planes de suscripción."""

    @abstractmethod
    async def save(self, plan: SubscriptionPlan, current_user_id: int) -> SubscriptionPlan:
        """Guardar o actualizar un plan de suscripción."""
        pass

    @abstractmethod
    async def get_by_id(self, plan_id: UUID, current_user_id: int) -> SubscriptionPlan | None:
        """Obtener suscripción por ID."""
        pass

    @abstractmethod
    async def get_by_payment_id(
        self, payment_id: str, current_user_id: int
    ) -> SubscriptionPlan | None:
        """Obtener suscripción por ID de pago (para idempotencia)."""
        pass

    @abstractmethod
    async def get_active_by_user(
        self, user_id: int, current_user_id: int
    ) -> SubscriptionPlan | None:
        """Obtener suscripción activa de un usuario."""
        pass

    @abstractmethod
    async def get_expiring_plans(self, days: int, current_user_id: int) -> list[SubscriptionPlan]:
        """Obtener planes que expiran en N días."""
        pass

    @abstractmethod
    async def get_expired_plans(self, current_user_id: int) -> list[SubscriptionPlan]:
        """Obtener todos los planes expirados."""
        pass

    @abstractmethod
    async def deactivate(self, plan_id: UUID, current_user_id: int) -> bool:
        """Desactivar un plan de suscripción."""
        pass

    @abstractmethod
    async def get_by_user_paginated(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
        current_user_id: int = 0,
    ) -> list[SubscriptionPlan]:
        """Obtener suscripciones de un usuario con paginación."""
        pass

    @abstractmethod
    async def count_by_user(self, user_id: int, current_user_id: int = 0) -> int:
        """Contar total de suscripciones de un usuario."""
        pass
