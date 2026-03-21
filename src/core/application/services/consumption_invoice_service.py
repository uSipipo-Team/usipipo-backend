"""
Servicio de gestión de facturas de consumo.

Este servicio se encarga de crear y gestionar facturas de consumo
cuando se cierra un ciclo de facturación.

Author: uSipipo Team
"""

import logging
import uuid
from decimal import Decimal

from usipipo_commons.domain.entities.consumption_billing import ConsumptionBilling
from usipipo_commons.domain.entities.consumption_invoice import ConsumptionInvoice
from usipipo_commons.domain.enums.billing_status import BillingStatus
from usipipo_commons.domain.enums.consumption_payment_method import ConsumptionPaymentMethod
from usipipo_commons.domain.enums.invoice_status import InvoiceStatus

from src.core.domain.interfaces.i_consumption_billing_repository import (
    IConsumptionBillingRepository,
)
from src.core.domain.interfaces.i_consumption_invoice_repository import (
    IConsumptionInvoiceRepository,
)
from src.core.domain.interfaces.i_user_repository import IUserRepository
from src.shared.config import settings

logger = logging.getLogger(__name__)


class ConsumptionInvoiceService:
    """
    Servicio para gestionar facturas de consumo.

    Responsabilidades:
    - Crear facturas al cerrar ciclos de facturación
    - Gestionar pagos de facturas
    - Verificar estado de facturas
    - Limpiar facturas expiradas
    """

    def __init__(
        self,
        invoice_repo: IConsumptionInvoiceRepository,
        billing_repo: IConsumptionBillingRepository,
        user_repo: IUserRepository,
    ):
        self.invoice_repo = invoice_repo
        self.billing_repo = billing_repo
        self.user_repo = user_repo
        self.stars_conversion_rate = Decimal(str(settings.TELEGRAM_STARS_TO_USD))

    async def create_invoice_from_billing(
        self,
        billing: ConsumptionBilling,
        payment_method: ConsumptionPaymentMethod = ConsumptionPaymentMethod.CRYPTO,
        current_user_id: int | None = None,
    ) -> ConsumptionInvoice:
        """
        Crea una factura de consumo desde un ciclo de facturación cerrado.

        Args:
            billing: Ciclo de facturación cerrado
            payment_method: Método de pago (crypto o stars)
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            ConsumptionInvoice: Factura creada

        Raises:
            ValueError: Si el ciclo no está cerrado o no tiene costo
        """
        if not billing.is_closed:
            raise ValueError("Solo se pueden crear facturas para ciclos cerrados")

        if billing.total_cost_usd <= 0:
            raise ValueError("El ciclo no tiene costo pendiente")

        # Verificar si ya existe una factura para este billing
        if billing.id:
            existing_invoices = await self.invoice_repo.get_by_billing(
                billing.id, current_user_id or billing.user_id
            )
            if existing_invoices:
                logger.info(f"Ya existe factura para billing {billing.id}")
                return existing_invoices[0]

        # Generar wallet address temporal para crypto
        wallet_address = f"0x{uuid.uuid4().hex[:40]}"

        # Crear factura
        invoice = ConsumptionInvoice(
            billing_id=billing.id or uuid.uuid4(),
            user_id=billing.user_id,
            amount_usd=billing.total_cost_usd,
            wallet_address=wallet_address,
            payment_method=payment_method,
            status=InvoiceStatus.PENDING,
        )

        # Guardar en BD
        saved_invoice = await self.invoice_repo.save(invoice, current_user_id or billing.user_id)

        logger.info(
            f"Factura creada - invoice_id={saved_invoice.id}, "
            f"billing_id={billing.id}, "
            f"user_id={billing.user_id}, "
            f"amount=${billing.total_cost_usd:.2f}"
        )

        return saved_invoice

    async def get_pending_invoice_for_user(
        self, user_id: int, current_user_id: int
    ) -> ConsumptionInvoice | None:
        """
        Obtiene la factura pendiente de un usuario.

        Args:
            user_id: ID del usuario
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            ConsumptionInvoice | None: Factura pendiente o None
        """
        return await self.invoice_repo.get_pending_by_user(user_id, current_user_id)

    async def pay_invoice(
        self,
        invoice_id: uuid.UUID,
        transaction_hash: str | None = None,
        telegram_payment_id: str | None = None,
        current_user_id: int | None = None,
    ) -> bool:
        """
        Marca una factura como pagada.

        Args:
            invoice_id: ID de la factura
            transaction_hash: Hash de transacción crypto (opcional)
            telegram_payment_id: ID de pago de Telegram Stars (opcional)
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            bool: True si se pagó exitosamente

        Raises:
            ValueError: Si no se proporciona método de pago válido
        """
        if not transaction_hash and not telegram_payment_id:
            raise ValueError("Se requiere transaction_hash o telegram_payment_id")

        # Obtener factura
        invoice = await self.invoice_repo.get_by_id(invoice_id, current_user_id or 0)

        if not invoice:
            logger.error(f"Factura {invoice_id} no encontrada")
            return False

        if invoice.status != InvoiceStatus.PENDING.value:
            logger.warning(f"Factura {invoice_id} no está pendiente")
            return False

        if invoice.is_expired:
            logger.warning(f"Factura {invoice_id} ha expirado")
            return False

        # Marcar como pagado
        hash_to_use = transaction_hash or ""
        success = await self.invoice_repo.mark_as_paid(
            invoice_id, hash_to_use, current_user_id or invoice.user_id
        )

        if success:
            logger.info(f"Factura pagada - invoice_id={invoice_id}")

            # Si hay un billing asociado, marcarlo como pagado también
            if success and invoice.billing_id:
                await self.billing_repo.update_status(
                    invoice.billing_id,
                    BillingStatus.PAID,
                    current_user_id or invoice.user_id,
                )

                # Actualizar usuario - quitar deuda
                user = await self.user_repo.get_by_telegram_id(invoice.user_id)
                if user:
                    user.clear_debt()
                    await self.user_repo.update(user)
                    logger.info(f"Deuda cancelada para usuario {invoice.user_id}")

        return success

    async def expire_overdue_invoices(self, current_user_id: int = 0) -> int:
        """
        Expira todas las facturas pendientes que han superado su tiempo de expiración.

        Args:
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            int: Cantidad de facturas expiradas
        """
        expired_invoices = await self.invoice_repo.get_expired_pending(current_user_id)

        expired_count = 0
        for invoice in expired_invoices:
            if invoice.id:
                success = await self.invoice_repo.mark_as_expired(invoice.id, current_user_id)
                if success:
                    expired_count += 1
                    logger.info(f"Factura expirada - invoice_id={invoice.id}")

        logger.info(f"Total facturas expiradas: {expired_count}")
        return expired_count

    async def get_invoice_with_payment_info(
        self, invoice_id: uuid.UUID, current_user_id: int
    ) -> dict | None:
        """
        Obtiene una factura con información de pago para mostrar al usuario.

        Args:
            invoice_id: ID de la factura
            current_user_id: ID del usuario actual (para auditoría)

        Returns:
            dict: Información de pago o None
        """
        invoice = await self.invoice_repo.get_by_id(invoice_id, current_user_id)

        if not invoice:
            return None

        return {
            "id": invoice.id,
            "amount_usd": str(invoice.amount_usd),
            "stars_amount": invoice.get_stars_amount()
            if invoice.payment_method == ConsumptionPaymentMethod.STARS
            else None,
            "wallet_address": invoice.wallet_address,
            "payment_method": invoice.payment_method.value,
            "status": invoice.status.value,
            "time_remaining_seconds": invoice.time_remaining_seconds,
            "time_remaining_formatted": invoice.time_remaining_formatted,
            "payment_instructions": invoice.get_payment_instructions(),
            "is_expired": invoice.is_expired,
        }
