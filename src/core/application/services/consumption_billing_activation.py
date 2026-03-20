"""
Servicio de activación y cancelación del modo consumo.

Contiene la lógica para activar y cancelar el modo consumo
de los usuarios, incluyendo validaciones y bloqueo de claves VPN.

Author: uSipipo Team
"""

import logging
from datetime import UTC, datetime
from decimal import Decimal

from usipipo_commons.domain.entities.consumption_billing import (
    BillingStatus,
    ConsumptionBilling,
)

from src.core.domain.interfaces.i_consumption_billing_repository import (
    IConsumptionBillingRepository,
)
from src.core.domain.interfaces.i_user_repository import IUserRepository

from .consumption_billing_dtos import ActivationResult, CancellationResult

logger = logging.getLogger(__name__)


class ConsumptionActivationService:
    """
    Servicio para activar y cancelar el modo consumo.

    Responsabilidades:
    - Validar si un usuario puede activar/cancelar modo consumo
    - Activar modo consumo creando un nuevo ciclo
    - Cancelar modo consumo cerrando el ciclo anticipadamente
    """

    def __init__(
        self,
        billing_repo: IConsumptionBillingRepository,
        user_repo: IUserRepository,
        price_per_mb: Decimal,
    ):
        self.billing_repo = billing_repo
        self.user_repo = user_repo
        self.price_per_mb = price_per_mb

    async def can_activate_consumption(
        self, user_id: int, current_user_id: int
    ) -> tuple[bool, str | None]:
        """
        Verifica si un usuario puede activar el modo consumo.

        Returns:
            Tuple de (puede_activar, mensaje_error)
        """
        user = await self.user_repo.get_by_telegram_id(user_id)
        if not user:
            return False, "Usuario no encontrado"

        if user.has_pending_debt:
            return False, (
                "Tienes una deuda pendiente. Debes pagarla antes de activar el modo consumo."
            )

        if user.consumption_mode_enabled:
            return False, "Ya tienes el modo consumo activo"

        # Verificar si ya tiene un ciclo activo
        existing_billing = await self.billing_repo.get_active_by_user(user_id, current_user_id)
        if existing_billing:
            return False, "Ya tienes un ciclo de consumo activo"

        return True, None

    async def activate_consumption_mode(
        self, user_id: int, current_user_id: int
    ) -> ActivationResult:
        """
        Activa el modo consumo para un usuario.

        Args:
            user_id: ID del usuario
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            ActivationResult con éxito o error
        """
        logger.info(f"Activando modo consumo para usuario {user_id}")

        try:
            # Validar que puede activar
            can_activate, error_msg = await self.can_activate_consumption(user_id, current_user_id)
            if not can_activate:
                logger.warning(f"No se puede activar modo consumo: {error_msg}")
                return ActivationResult(success=False, error_message=error_msg)

            # Crear nuevo ciclo de facturación
            billing = ConsumptionBilling(
                user_id=user_id,
                started_at=datetime.now(UTC),
                status=BillingStatus.ACTIVE,
                price_per_mb_usd=self.price_per_mb,
            )

            saved_billing = await self.billing_repo.save(billing, current_user_id)

            # Verificar que el billing tiene ID
            if saved_billing.id is None:
                return ActivationResult(
                    success=False,
                    error_message="Error al crear el ciclo de facturación",
                )

            billing_id = saved_billing.id  # ya verificamos que no es None

            # Actualizar usuario
            user = await self.user_repo.get_by_telegram_id(user_id)
            if user:
                user.activate_consumption_mode(billing_id)
                await self.user_repo.update(user)

            logger.info(f"Modo consumo activado - user_id={user_id}, billing_id={saved_billing.id}")

            return ActivationResult(success=True, billing_id=saved_billing.id)

        except Exception as e:
            logger.error(f"Error activando modo consumo: {e}")
            return ActivationResult(
                success=False, error_message="Error interno al activar el modo consumo"
            )

    async def can_cancel_consumption(
        self, user_id: int, current_user_id: int
    ) -> tuple[bool, str | None]:
        """
        Verifica si un usuario puede cancelar el modo consumo.

        Args:
            user_id: ID del usuario
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            Tuple de (puede_cancelar, mensaje_error)
        """
        user = await self.user_repo.get_by_telegram_id(user_id)
        if not user:
            return False, "Usuario no encontrado"

        # Verificar que tiene un ciclo activo (fuente de verdad principal)
        billing = await self.billing_repo.get_active_by_user(user_id, current_user_id)
        if not billing:
            return False, "No tienes un ciclo de consumo activo"

        if user.has_pending_debt:
            return (
                False,
                "Ya tienes una deuda pendiente. Debes pagarla antes de cancelar.",
            )

        return True, None

    async def cancel_consumption_mode(
        self, user_id: int, current_user_id: int
    ) -> CancellationResult:
        """
        Cancela el modo consumo para un usuario, cerrando el ciclo anticipadamente.

        Args:
            user_id: ID del usuario
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            CancellationResult con éxito o error y detalles del ciclo
        """
        logger.info(f"Cancelando modo consumo para usuario {user_id}")

        try:
            # Validar que puede cancelar
            can_cancel, error_msg = await self.can_cancel_consumption(user_id, current_user_id)
            if not can_cancel:
                logger.warning(f"No se puede cancelar modo consumo: {error_msg}")
                return CancellationResult(success=False, error_message=error_msg)

            # Obtener ciclo activo
            billing = await self.billing_repo.get_active_by_user(user_id, current_user_id)
            if not billing or billing.id is None:
                return CancellationResult(
                    success=False,
                    error_message="No se encontró el ciclo de consumo activo",
                )

            billing_id = billing.id

            # Calcular días activos antes de cerrar
            days_active = 0
            if billing.started_at:
                delta = datetime.now(UTC) - billing.started_at
                days_active = delta.days

            # Guardar datos antes de cerrar
            mb_consumed = billing.mb_consumed
            total_cost = billing.total_cost_usd

            # Determinar si hay deuda real
            has_debt = mb_consumed > 0 or total_cost > 0

            # Cerrar ciclo
            billing.close_cycle()
            success = await self.billing_repo.update_status(
                billing_id, BillingStatus.CLOSED, current_user_id
            )

            if not success:
                return CancellationResult(
                    success=False,
                    error_message="Error al cerrar el ciclo de facturación",
                )

            # Solo bloquear claves y marcar deuda si realmente hay algo que cobrar
            if has_debt:
                await self._handle_cancellation_with_debt(
                    user_id,
                    billing_id,
                    mb_consumed,
                    total_cost,
                    days_active,
                    current_user_id,
                )
            else:
                await self._handle_cancellation_without_debt(
                    user_id, billing_id, days_active, current_user_id
                )

            return CancellationResult(
                success=True,
                billing_id=billing_id,
                mb_consumed=mb_consumed,
                total_cost_usd=total_cost,
                days_active=days_active,
                had_debt=has_debt,
            )

        except Exception as e:
            logger.error(f"Error cancelando modo consumo: {e}")
            return CancellationResult(
                success=False, error_message="Error interno al cancelar el modo consumo"
            )

    async def _handle_cancellation_with_debt(
        self,
        user_id: int,
        billing_id,
        mb_consumed: Decimal,
        total_cost: Decimal,
        days_active: int,
        current_user_id: int,
    ) -> None:
        """Maneja la cancelación cuando hay deuda pendiente."""
        user = await self.user_repo.get_by_telegram_id(user_id)
        if user:
            user.mark_as_has_debt()
            await self.user_repo.update(user)

            # Bloquear todas las claves del usuario
            # Note: VPN integration would be handled via dependency injection
            # in a full implementation. For now, this is a placeholder.
            logger.warning(
                f"VPN key blocking not implemented - user {user_id} has debt: "
                f"mb={mb_consumed:.2f}, cost=${total_cost:.2f}"
            )

        logger.info(
            f"Modo consumo cancelado con deuda - billing_id={billing_id}, "
            f"user_id={user_id}, "
            f"mb_consumed={mb_consumed:.2f}, "
            f"cost=${total_cost:.2f}, "
            f"days_active={days_active}"
        )

    async def _handle_cancellation_without_debt(
        self,
        user_id: int,
        billing_id,
        days_active: int,
        current_user_id: int,
    ) -> None:
        """Maneja la cancelación cuando no hay deuda."""
        user = await self.user_repo.get_by_telegram_id(user_id)
        if user:
            user.deactivate_consumption_mode()
            await self.user_repo.update(user)

        logger.info(
            f"Modo consumo cancelado sin deuda - billing_id={billing_id}, "
            f"user_id={user_id}, "
            f"days_active={days_active}. "
            f"Claves VPN NO bloqueadas."
        )
