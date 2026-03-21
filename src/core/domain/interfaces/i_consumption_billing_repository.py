"""Interfaces de repositorio para la capa de dominio."""

import uuid
from abc import ABC, abstractmethod

from usipipo_commons.domain.entities.consumption_billing import (
    BillingStatus,
    ConsumptionBilling,
)


class IConsumptionBillingRepository(ABC):
    """
    Contrato para la persistencia de ciclos de facturación por consumo.
    Define cómo interactuamos con la tabla de billing en la BD.
    """

    @abstractmethod
    async def save(self, billing: ConsumptionBilling, current_user_id: int) -> ConsumptionBilling:
        """Guarda un nuevo ciclo de facturación o actualiza uno existente."""
        pass

    @abstractmethod
    async def get_by_id(
        self, billing_id: uuid.UUID, current_user_id: int
    ) -> ConsumptionBilling | None:
        """Busca un ciclo de facturación específico por su ID."""
        pass

    @abstractmethod
    async def get_by_user(self, user_id: int, current_user_id: int) -> list[ConsumptionBilling]:
        """Recupera todos los ciclos de facturación de un usuario."""
        pass

    @abstractmethod
    async def get_active_by_user(
        self, user_id: int, current_user_id: int
    ) -> ConsumptionBilling | None:
        """
        Recupera el ciclo de facturación activo de un usuario.
        Solo puede haber uno activo por usuario.
        """
        pass

    @abstractmethod
    async def get_by_status(
        self, status: BillingStatus, current_user_id: int
    ) -> list[ConsumptionBilling]:
        """Recupera todos los ciclos con un estado específico."""
        pass

    @abstractmethod
    async def get_expired_active_cycles(
        self, days: int, current_user_id: int
    ) -> list[ConsumptionBilling]:
        """
        Recupera ciclos activos que han excedido el límite de días.
        Útil para el cron job de cierre automático.
        """
        pass

    @abstractmethod
    async def update_status(
        self, billing_id: uuid.UUID, status: BillingStatus, current_user_id: int
    ) -> bool:
        """Actualiza el estado de un ciclo de facturación."""
        pass

    @abstractmethod
    async def add_consumption(
        self, billing_id: uuid.UUID, mb_used: float, current_user_id: int
    ) -> bool:
        """Agrega consumo a un ciclo activo."""
        pass

    @abstractmethod
    async def delete(self, billing_id: uuid.UUID, current_user_id: int) -> bool:
        """Elimina un ciclo de facturación de la base de datos."""
        pass
