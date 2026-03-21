"""
Servicio de gestión de ciclos de facturación por consumo.

Contiene la lógica para cerrar ciclos, registrar consumo,
marcar pagos y consultar historial de facturación.

Author: uSipipo Team
"""

import logging
import uuid
from datetime import UTC, datetime

from usipipo_commons.domain.entities.consumption_billing import (
    BillingStatus,
    ConsumptionBilling,
)
from usipipo_commons.domain.enums.consumption_payment_method import ConsumptionPaymentMethod

from src.core.domain.interfaces.i_consumption_billing_repository import (
    IConsumptionBillingRepository,
)
from src.core.domain.interfaces.i_consumption_invoice_repository import (
    IConsumptionInvoiceRepository,
)
from src.core.domain.interfaces.i_user_repository import IUserRepository

from .consumption_billing_dtos import ConsumptionSummary

logger = logging.getLogger(__name__)


class ConsumptionCycleService:
    """
    Servicio para gestionar ciclos de facturación por consumo.

    Responsabilidades:
    - Registrar consumo de datos
    - Cerrar ciclos de facturación
    - Marcar ciclos como pagados
    - Consultar consumo actual e historial
    - Obtener ciclos expirados
    """

    def __init__(
        self,
        billing_repo: IConsumptionBillingRepository,
        user_repo: IUserRepository,
        cycle_days: int,
        invoice_repo: IConsumptionInvoiceRepository | None = None,
    ):
        self.billing_repo = billing_repo
        self.user_repo = user_repo
        self.cycle_days = cycle_days
        self.invoice_repo = invoice_repo

    async def record_data_usage(self, user_id: int, mb_used: float, current_user_id: int) -> bool:
        """
        Registra consumo de datos para un usuario en modo consumo.

        Args:
            user_id: ID del usuario
            mb_used: MB consumidos
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            True si se registró exitosamente
        """
        try:
            # Obtener ciclo activo
            billing = await self.billing_repo.get_active_by_user(user_id, current_user_id)

            if not billing:
                logger.debug(f"Usuario {user_id} no tiene ciclo de consumo activo")
                return False

            if billing.id is None:
                logger.error(f"Ciclo de consumo para usuario {user_id} no tiene ID")
                return False

            # Agregar consumo
            success = await self.billing_repo.add_consumption(billing.id, mb_used, current_user_id)

            if success:
                logger.debug(f"Consumo registrado - user_id={user_id}, mb_used={mb_used:.2f}")

            return success

        except Exception as e:
            logger.error(f"Error registrando consumo: {e}")
            return False

    async def get_current_consumption(
        self, user_id: int, current_user_id: int
    ) -> ConsumptionSummary | None:
        """
        Obtiene el resumen de consumo actual de un usuario.

        Args:
            user_id: ID del usuario
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            ConsumptionSummary o None si no tiene ciclo activo
        """
        try:
            billing = await self.billing_repo.get_active_by_user(user_id, current_user_id)

            if not billing:
                # Verificar si tiene ciclo cerrado (deuda pendiente)
                user = await self.user_repo.get_by_telegram_id(user_id)
                if user and user.current_billing_id:
                    billing = await self.billing_repo.get_by_id(
                        user.current_billing_id, current_user_id
                    )

                if not billing:
                    return None

            # Calcular días activos
            days_active = 0
            if billing.started_at:
                delta = datetime.now(UTC) - billing.started_at
                days_active = delta.days

            return ConsumptionSummary(
                billing_id=billing.id,
                mb_consumed=billing.mb_consumed,
                gb_consumed=billing.gb_consumed,
                total_cost_usd=billing.total_cost_usd,
                days_active=days_active,
                is_active=billing.is_active,
                formatted_cost=billing.get_formatted_cost(),
                formatted_consumption=billing.get_formatted_consumption(),
            )

        except Exception as e:
            logger.error(f"Error obteniendo consumo: {e}")
            return None

    async def close_billing_cycle(self, billing_id: uuid.UUID, current_user_id: int) -> bool:
        """
        Cierra un ciclo de facturación y crea la factura correspondiente.

        Args:
            billing_id: ID del ciclo a cerrar
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            True si se cerró exitosamente
        """
        try:
            billing = await self.billing_repo.get_by_id(billing_id, current_user_id)
            if not billing:
                logger.error(f"Ciclo {billing_id} no encontrado")
                return False

            if not billing.is_active:
                logger.warning(f"Ciclo {billing_id} ya no está activo")
                return False

            # Cerrar ciclo en la entidad
            billing.close_cycle()

            # Actualizar en BD
            success = await self.billing_repo.update_status(
                billing_id, BillingStatus.CLOSED, current_user_id
            )

            if success:
                # Actualizar usuario
                user = await self.user_repo.get_by_telegram_id(billing.user_id)
                if user:
                    user.mark_as_has_debt()
                    await self.user_repo.update(user)

                    # Note: VPN key blocking would be handled via dependency injection
                    # in a full implementation. For now, this is a placeholder.
                    logger.warning(
                        f"VPN key blocking not implemented - user {billing.user_id} "
                        f"has debt: ${billing.total_cost_usd:.2f}"
                    )

                # Crear factura si hay invoice_repo
                if self.invoice_repo and billing.total_cost_usd > 0:
                    from usipipo_commons.domain.entities.consumption_invoice import (
                        ConsumptionInvoice,
                    )
                    from usipipo_commons.domain.enums.invoice_status import InvoiceStatus

                    invoice = ConsumptionInvoice(
                        billing_id=billing_id,
                        user_id=billing.user_id,
                        amount_usd=billing.total_cost_usd,
                        wallet_address=f"0x{uuid.uuid4().hex[:40]}",
                        payment_method=ConsumptionPaymentMethod.CRYPTO,
                        status=InvoiceStatus.PENDING,
                    )
                    await self.invoice_repo.save(invoice, current_user_id)
                    logger.info(
                        f"Factura creada - billing_id={billing_id}, "
                        f"user_id={billing.user_id}, "
                        f"amount=${billing.total_cost_usd:.2f}"
                    )

                logger.info(
                    f"Ciclo cerrado - billing_id={billing_id}, "
                    f"user_id={billing.user_id}, "
                    f"cost=${billing.total_cost_usd:.2f}"
                )

            return success

        except Exception as e:
            logger.error(f"Error cerrando ciclo: {e}")
            return False

    async def mark_cycle_as_paid(self, billing_id: uuid.UUID, current_user_id: int) -> bool:
        """
        Marca un ciclo como pagado.

        Args:
            billing_id: ID del ciclo
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            True si se actualizó exitosamente
        """
        try:
            billing = await self.billing_repo.get_by_id(billing_id, current_user_id)
            if not billing:
                return False

            if not billing.is_closed:
                logger.warning(f"No se puede pagar ciclo {billing_id} - no está cerrado")
                return False

            # Actualizar estado
            success = await self.billing_repo.update_status(
                billing_id, BillingStatus.PAID, current_user_id
            )

            if success:
                logger.info(f"Ciclo marcado como pagado - billing_id={billing_id}")

                # Actualizar usuario - quitar deuda y desbloquear claves
                user = await self.user_repo.get_by_telegram_id(billing.user_id)
                if user:
                    user.clear_debt()
                    await self.user_repo.update(user)

                    # Note: VPN key unblocking would be handled via dependency injection
                    logger.info(f"Deuda cancelada para usuario {billing.user_id}")

            return success

        except Exception as e:
            logger.error(f"Error marcando ciclo como pagado: {e}")
            return False

    async def get_billing_history(
        self, user_id: int, current_user_id: int
    ) -> list[ConsumptionSummary]:
        """
        Obtiene el historial de facturación de un usuario.

        Args:
            user_id: ID del usuario
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            Lista de ConsumptionSummary ordenada por fecha (más reciente primero)
        """
        try:
            billings = await self.billing_repo.get_by_user(user_id, current_user_id)

            summaries = []
            for billing in billings:
                if billing.id is None:
                    continue

                # Calcular días activos
                days_active = 0
                if billing.started_at:
                    if billing.ended_at:
                        delta = billing.ended_at - billing.started_at
                    else:
                        delta = datetime.now(UTC) - billing.started_at
                    days_active = delta.days

                summaries.append(
                    ConsumptionSummary(
                        billing_id=billing.id,
                        mb_consumed=billing.mb_consumed,
                        gb_consumed=billing.gb_consumed,
                        total_cost_usd=billing.total_cost_usd,
                        days_active=days_active,
                        is_active=billing.is_active,
                        formatted_cost=billing.get_formatted_cost(),
                        formatted_consumption=billing.get_formatted_consumption(),
                    )
                )

            # Ordenar por fecha de inicio (más reciente primero)
            summaries.sort(key=lambda x: x.days_active, reverse=True)
            return summaries

        except Exception as e:
            logger.error(f"Error obteniendo historial de facturación: {e}")
            return []

    async def get_expired_active_cycles(self, current_user_id: int) -> list[ConsumptionBilling]:
        """
        Obtiene ciclos activos que han excedido el período de ciclo.

        Args:
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            Lista de ciclos expirados
        """
        try:
            return await self.billing_repo.get_expired_active_cycles(
                self.cycle_days, current_user_id
            )
        except Exception as e:
            logger.error(f"Error obteniendo ciclos expirados: {e}")
            return []
