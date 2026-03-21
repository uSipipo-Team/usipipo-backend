"""Routes para gestión de facturas de consumo."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.user import User
from usipipo_commons.domain.enums.invoice_status import InvoiceStatus

from src.infrastructure.api.v1.deps import get_current_user, get_db
from src.infrastructure.persistence.repositories.consumption_invoice_repository import (
    ConsumptionInvoiceRepository,
)
from src.shared.schemas.consumption_invoice import (
    ConsumptionInvoiceCreateRequest,
    ConsumptionInvoiceListResponse,
    ConsumptionInvoicePaymentRequest,
    ConsumptionInvoiceResponse,
    ConsumptionInvoiceStatusUpdateRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/invoices", tags=["Consumption Invoices"])


def _get_invoice_repo(session: AsyncSession) -> ConsumptionInvoiceRepository:
    """Obtiene el repositorio de facturas."""
    return ConsumptionInvoiceRepository(session)


@router.post(
    "",
    response_model=ConsumptionInvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Consumption Invoice",
)
async def create_consumption_invoice(
    request: ConsumptionInvoiceCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Crea una nueva factura de consumo para un usuario.

    Requiere autenticación JWT.

    Args:
        request: Datos de la factura a crear
        current_user: Usuario autenticado
        session: Sesión de base de datos

    Returns:
        ConsumptionInvoiceResponse: Factura creada

    Raises:
        HTTPException: 400 si hay error en la creación
    """
    try:
        from usipipo_commons.domain.entities.consumption_invoice import ConsumptionInvoice
        from usipipo_commons.domain.enums.consumption_payment_method import (
            ConsumptionPaymentMethod,
        )

        invoice = ConsumptionInvoice(
            billing_id=request.billing_id,
            user_id=request.user_id,
            amount_usd=request.amount_usd,
            wallet_address=f"0x{uuid.uuid4().hex[:40]}",  # Generar wallet temporal
            payment_method=ConsumptionPaymentMethod(request.payment_method),
        )

        repo = _get_invoice_repo(session)
        created = await repo.save(invoice, current_user.telegram_id)

        return ConsumptionInvoiceResponse(
            id=created.id,
            billing_id=created.billing_id,
            user_id=created.user_id,
            amount_usd=created.amount_usd,
            wallet_address=created.wallet_address,
            payment_method=created.payment_method.value,
            status=created.status.value,
            expires_at=created.expires_at,
            paid_at=created.paid_at,
            transaction_hash=created.transaction_hash,
            telegram_payment_id=created.telegram_payment_id,
            created_at=created.created_at,
            time_remaining_seconds=created.time_remaining_seconds,
            is_expired=created.is_expired,
        )
    except ValueError as e:
        logger.warning(f"Invalid payment method: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating consumption invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invoice: {str(e)}",
        )


@router.get(
    "/{invoice_id}",
    response_model=ConsumptionInvoiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Invoice by ID",
)
async def get_consumption_invoice(
    invoice_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Obtiene una factura de consumo por su ID.

    Requiere autenticación JWT.

    Args:
        invoice_id: UUID de la factura
        current_user: Usuario autenticado
        session: Sesión de base de datos

    Returns:
        ConsumptionInvoiceResponse: Factura encontrada

    Raises:
        HTTPException: 404 si no se encuentra la factura
    """
    repo = _get_invoice_repo(session)
    invoice = await repo.get_by_id(invoice_id, current_user.telegram_id)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found",
        )

    return ConsumptionInvoiceResponse(
        id=invoice.id,
        billing_id=invoice.billing_id,
        user_id=invoice.user_id,
        amount_usd=invoice.amount_usd,
        wallet_address=invoice.wallet_address,
        payment_method=invoice.payment_method.value,
        status=invoice.status.value,
        expires_at=invoice.expires_at,
        paid_at=invoice.paid_at,
        transaction_hash=invoice.transaction_hash,
        telegram_payment_id=invoice.telegram_payment_id,
        created_at=invoice.created_at,
        time_remaining_seconds=invoice.time_remaining_seconds,
        is_expired=invoice.is_expired,
    )


@router.get(
    "/user/{user_id}",
    response_model=ConsumptionInvoiceListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User Invoices",
)
async def get_user_consumption_invoices(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Obtiene todas las facturas de consumo de un usuario.

    Requiere autenticación JWT.

    Args:
        user_id: ID del usuario (telegram_id)
        current_user: Usuario autenticado
        session: Sesión de base de datos

    Returns:
        ConsumptionInvoiceListResponse: Lista de facturas con contadores
    """
    repo = _get_invoice_repo(session)
    invoices = await repo.get_by_user(user_id, current_user.telegram_id)

    pending_count = sum(1 for inv in invoices if inv.status == InvoiceStatus.PENDING.value)
    paid_count = sum(1 for inv in invoices if inv.status == InvoiceStatus.PAID.value)
    expired_count = sum(1 for inv in invoices if inv.status == InvoiceStatus.EXPIRED.value)

    return ConsumptionInvoiceListResponse(
        invoices=[
            ConsumptionInvoiceResponse(
                id=inv.id,
                billing_id=inv.billing_id,
                user_id=inv.user_id,
                amount_usd=inv.amount_usd,
                wallet_address=inv.wallet_address,
                payment_method=inv.payment_method.value,
                status=inv.status.value,
                expires_at=inv.expires_at,
                paid_at=inv.paid_at,
                transaction_hash=inv.transaction_hash,
                telegram_payment_id=inv.telegram_payment_id,
                created_at=inv.created_at,
                time_remaining_seconds=inv.time_remaining_seconds,
                is_expired=inv.is_expired,
            )
            for inv in invoices
        ],
        total=len(invoices),
        pending_count=pending_count,
        paid_count=paid_count,
        expired_count=expired_count,
    )


@router.get(
    "/user/{user_id}/pending",
    response_model=ConsumptionInvoiceResponse | None,
    status_code=status.HTTP_200_OK,
    summary="Get User Pending Invoice",
)
async def get_user_pending_invoice(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Obtiene la factura pendiente de un usuario (máximo 1 activa).

    Requiere autenticación JWT.

    Args:
        user_id: ID del usuario (telegram_id)
        current_user: Usuario autenticado
        session: Sesión de base de datos

    Returns:
        ConsumptionInvoiceResponse | None: Factura pendiente o None
    """
    repo = _get_invoice_repo(session)
    invoice = await repo.get_pending_by_user(user_id, current_user.telegram_id)

    if not invoice:
        return None

    return ConsumptionInvoiceResponse(
        id=invoice.id,
        billing_id=invoice.billing_id,
        user_id=invoice.user_id,
        amount_usd=invoice.amount_usd,
        wallet_address=invoice.wallet_address,
        payment_method=invoice.payment_method.value,
        status=invoice.status.value,
        expires_at=invoice.expires_at,
        paid_at=invoice.paid_at,
        transaction_hash=invoice.transaction_hash,
        telegram_payment_id=invoice.telegram_payment_id,
        created_at=invoice.created_at,
        time_remaining_seconds=invoice.time_remaining_seconds,
        is_expired=invoice.is_expired,
    )


@router.get(
    "/billing/{billing_id}",
    response_model=list[ConsumptionInvoiceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Billing Cycle Invoices",
)
async def get_billing_cycle_invoices(
    billing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Obtiene todas las facturas asociadas a un ciclo de facturación.

    Requiere autenticación JWT.

    Args:
        billing_id: UUID del ciclo de facturación
        current_user: Usuario autenticado
        session: Sesión de base de datos

    Returns:
        list[ConsumptionInvoiceResponse]: Lista de facturas del ciclo
    """
    repo = _get_invoice_repo(session)
    invoices = await repo.get_by_billing(billing_id, current_user.telegram_id)

    return [
        ConsumptionInvoiceResponse(
            id=inv.id,
            billing_id=inv.billing_id,
            user_id=inv.user_id,
            amount_usd=inv.amount_usd,
            wallet_address=inv.wallet_address,
            payment_method=inv.payment_method.value,
            status=inv.status.value,
            expires_at=inv.expires_at,
            paid_at=inv.paid_at,
            transaction_hash=inv.transaction_hash,
            telegram_payment_id=inv.telegram_payment_id,
            created_at=inv.created_at,
            time_remaining_seconds=inv.time_remaining_seconds,
            is_expired=inv.is_expired,
        )
        for inv in invoices
    ]


@router.post(
    "/{invoice_id}/pay",
    response_model=ConsumptionInvoiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark Invoice as Paid",
)
async def mark_invoice_as_paid(
    invoice_id: uuid.UUID,
    request: ConsumptionInvoicePaymentRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Marca una factura como pagada con hash de transacción o Telegram payment ID.

    Requiere autenticación JWT.

    Args:
        invoice_id: UUID de la factura
        request: Datos de pago (transaction_hash o telegram_payment_id)
        current_user: Usuario autenticado
        session: Sesión de base de datos

    Returns:
        ConsumptionInvoiceResponse: Factura actualizada

    Raises:
        HTTPException: 400 si la factura no está pendiente o está expirada
        HTTPException: 404 si no se encuentra la factura
    """
    repo = _get_invoice_repo(session)
    invoice = await repo.get_by_id(invoice_id, current_user.telegram_id)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found",
        )

    if invoice.status != InvoiceStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice is not pending payment",
        )

    if invoice.is_expired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice has expired",
        )

    # Determinar qué método de pago usar
    transaction_hash = request.transaction_hash or ""

    success = await repo.mark_as_paid(invoice_id, transaction_hash, current_user.telegram_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark invoice as paid",
        )

    # Recargar la factura actualizada
    updated_invoice = await repo.get_by_id(invoice_id, current_user.telegram_id)

    if not updated_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    return ConsumptionInvoiceResponse(
        id=updated_invoice.id,
        billing_id=updated_invoice.billing_id,
        user_id=updated_invoice.user_id,
        amount_usd=updated_invoice.amount_usd,
        wallet_address=updated_invoice.wallet_address,
        payment_method=updated_invoice.payment_method.value,
        status=updated_invoice.status.value,
        expires_at=updated_invoice.expires_at,
        paid_at=updated_invoice.paid_at,
        transaction_hash=updated_invoice.transaction_hash,
        telegram_payment_id=updated_invoice.telegram_payment_id,
        created_at=updated_invoice.created_at,
        time_remaining_seconds=updated_invoice.time_remaining_seconds,
        is_expired=updated_invoice.is_expired,
    )


@router.post(
    "/{invoice_id}/expire",
    response_model=ConsumptionInvoiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark Invoice as Expired",
)
async def mark_invoice_as_expired(
    invoice_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Marca una factura como expirada.

    Requiere autenticación JWT. Solo admins deberían llamar a este endpoint.

    Args:
        invoice_id: UUID de la factura
        current_user: Usuario autenticado
        session: Sesión de base de datos

    Returns:
        ConsumptionInvoiceResponse: Factura actualizada

    Raises:
        HTTPException: 400 si la factura ya está pagada
        HTTPException: 404 si no se encuentra la factura
    """
    repo = _get_invoice_repo(session)
    invoice = await repo.get_by_id(invoice_id, current_user.telegram_id)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found",
        )

    if invoice.status == InvoiceStatus.PAID.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot expire a paid invoice",
        )

    success = await repo.mark_as_expired(invoice_id, current_user.telegram_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark invoice as expired",
        )

    # Recargar la factura actualizada
    updated_invoice = await repo.get_by_id(invoice_id, current_user.telegram_id)

    if not updated_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    return ConsumptionInvoiceResponse(
        id=updated_invoice.id,
        billing_id=updated_invoice.billing_id,
        user_id=updated_invoice.user_id,
        amount_usd=updated_invoice.amount_usd,
        wallet_address=updated_invoice.wallet_address,
        payment_method=updated_invoice.payment_method.value,
        status=updated_invoice.status.value,
        expires_at=updated_invoice.expires_at,
        paid_at=updated_invoice.paid_at,
        transaction_hash=updated_invoice.transaction_hash,
        telegram_payment_id=updated_invoice.telegram_payment_id,
        created_at=updated_invoice.created_at,
        time_remaining_seconds=updated_invoice.time_remaining_seconds,
        is_expired=updated_invoice.is_expired,
    )


@router.post(
    "/{invoice_id}/status",
    response_model=ConsumptionInvoiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Invoice Status",
)
async def update_invoice_status(
    invoice_id: uuid.UUID,
    request: ConsumptionInvoiceStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Actualiza el estado de una factura.

    Requiere autenticación JWT.

    Args:
        invoice_id: UUID de la factura
        request: Nuevo estado (pending, paid, expired)
        current_user: Usuario autenticado
        session: Sesión de base de datos

    Returns:
        ConsumptionInvoiceResponse: Factura actualizada

    Raises:
        HTTPException: 400 si el estado es inválido
        HTTPException: 404 si no se encuentra la factura
    """
    try:
        status_enum = InvoiceStatus(request.status.lower())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {request.status}. Must be one of: pending, paid, expired",
        ) from e

    repo = _get_invoice_repo(session)
    invoice = await repo.get_by_id(invoice_id, current_user.telegram_id)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found",
        )

    success = await repo.update_status(invoice_id, status_enum, current_user.telegram_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update invoice status",
        )

    # Recargar la factura actualizada
    updated_invoice = await repo.get_by_id(invoice_id, current_user.telegram_id)

    if not updated_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    return ConsumptionInvoiceResponse(
        id=updated_invoice.id,
        billing_id=updated_invoice.billing_id,
        user_id=updated_invoice.user_id,
        amount_usd=updated_invoice.amount_usd,
        wallet_address=updated_invoice.wallet_address,
        payment_method=updated_invoice.payment_method.value,
        status=updated_invoice.status.value,
        expires_at=updated_invoice.expires_at,
        paid_at=updated_invoice.paid_at,
        transaction_hash=updated_invoice.transaction_hash,
        telegram_payment_id=updated_invoice.telegram_payment_id,
        created_at=updated_invoice.created_at,
        time_remaining_seconds=updated_invoice.time_remaining_seconds,
        is_expired=updated_invoice.is_expired,
    )


@router.delete(
    "/{invoice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Invoice",
)
async def delete_consumption_invoice(
    invoice_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Elimina una factura de consumo.

    Requiere autenticación JWT. Usar con precaución.

    Args:
        invoice_id: UUID de la factura
        current_user: Usuario autenticado
        session: Sesión de base de datos

    Raises:
        HTTPException: 404 si no se encuentra la factura
    """
    repo = _get_invoice_repo(session)
    invoice = await repo.get_by_id(invoice_id, current_user.telegram_id)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found",
        )

    success = await repo.delete(invoice_id, current_user.telegram_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete invoice",
        )

    return None


@router.get(
    "/status/{invoice_status}",
    response_model=list[ConsumptionInvoiceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Invoices by Status",
)
async def get_invoices_by_status(
    invoice_status: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Obtiene todas las facturas con un estado específico.

    Requiere autenticación JWT.

    Args:
        invoice_status: Estado a filtrar (pending, paid, expired)
        current_user: Usuario autenticado
        session: Sesión de base de datos

    Returns:
        list[ConsumptionInvoiceResponse]: Lista de facturas filtradas

    Raises:
        HTTPException: 400 si el estado es inválido
    """
    try:
        status_enum = InvoiceStatus(invoice_status.lower())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {invoice_status}. Must be one of: pending, paid, expired",
        ) from e

    repo = _get_invoice_repo(session)
    invoices = await repo.get_by_status(status_enum, current_user.telegram_id)

    return [
        ConsumptionInvoiceResponse(
            id=inv.id,
            billing_id=inv.billing_id,
            user_id=inv.user_id,
            amount_usd=inv.amount_usd,
            wallet_address=inv.wallet_address,
            payment_method=inv.payment_method.value,
            status=inv.status.value,
            expires_at=inv.expires_at,
            paid_at=inv.paid_at,
            transaction_hash=inv.transaction_hash,
            telegram_payment_id=inv.telegram_payment_id,
            created_at=inv.created_at,
            time_remaining_seconds=inv.time_remaining_seconds,
            is_expired=inv.is_expired,
        )
        for inv in invoices
    ]


@router.get(
    "/expired/pending",
    response_model=list[ConsumptionInvoiceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Expired Pending Invoices",
)
async def get_expired_pending_invoices(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Obtiene todas las facturas pendientes que han expirado.

    Útil para limpieza periódica o jobs programados.
    Requiere autenticación JWT.

    Args:
        current_user: Usuario autenticado
        session: Sesión de base de datos

    Returns:
        list[ConsumptionInvoiceResponse]: Lista de facturas expiradas pendientes
    """
    repo = _get_invoice_repo(session)
    invoices = await repo.get_expired_pending(current_user.telegram_id)

    return [
        ConsumptionInvoiceResponse(
            id=inv.id,
            billing_id=inv.billing_id,
            user_id=inv.user_id,
            amount_usd=inv.amount_usd,
            wallet_address=inv.wallet_address,
            payment_method=inv.payment_method.value,
            status=inv.status.value,
            expires_at=inv.expires_at,
            paid_at=inv.paid_at,
            transaction_hash=inv.transaction_hash,
            telegram_payment_id=inv.telegram_payment_id,
            created_at=inv.created_at,
            time_remaining_seconds=inv.time_remaining_seconds,
            is_expired=inv.is_expired,
        )
        for inv in invoices
    ]
