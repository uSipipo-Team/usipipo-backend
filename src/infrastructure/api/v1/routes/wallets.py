"""Routes para gestión de wallets BSC."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from usipipo_commons.domain.entities.user import User

from src.core.application.services.wallet_management_service import WalletManagementService
from src.core.application.services.wallet_pool_service import WalletPoolService
from src.infrastructure.api.v1.deps import (
    get_current_user,
    get_wallet_management_service,
    get_wallet_pool_service,
)
from src.shared.schemas.wallet import (
    WalletCreateRequest,
    WalletDepositRequest,
    WalletPoolResponse,
    WalletPoolStats,
    WalletResponse,
    WalletUpdateRequest,
    WalletWithdrawRequest,
)

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.get(
    "/me",
    response_model=WalletResponse | None,
    status_code=status.HTTP_200_OK,
)
async def get_my_wallet(
    current_user: User = Depends(get_current_user),
    wallet_service: WalletManagementService = Depends(get_wallet_management_service),
):
    """
    Obtiene la wallet del usuario autenticado.

    Args:
        current_user: Usuario autenticado
        wallet_service: Servicio de Wallet

    Returns:
        WalletResponse: Wallet del usuario o None si no tiene
    """
    wallet = await wallet_service.get_wallet(current_user.id)
    return wallet


@router.get(
    "/{wallet_id}",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
)
async def get_wallet(
    wallet_id: UUID,
    current_user: User = Depends(get_current_user),
    wallet_service: WalletManagementService = Depends(get_wallet_management_service),
):
    """
    Obtiene una wallet por ID.

    Args:
        wallet_id: UUID de la wallet
        current_user: Usuario autenticado
        wallet_service: Servicio de Wallet

    Returns:
        WalletResponse: Wallet solicitada

    Raises:
        HTTPException: 404 si no existe la wallet
    """
    wallet = await wallet_service.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Verificar que el usuario sea dueño de la wallet
    if wallet.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this wallet")

    return wallet


@router.post(
    "",
    response_model=WalletResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_wallet(
    request: WalletCreateRequest,
    current_user: User = Depends(get_current_user),
    wallet_service: WalletManagementService = Depends(get_wallet_management_service),
    pool_service: WalletPoolService = Depends(get_wallet_pool_service),
):
    """
    Crea/asigna una nueva wallet al usuario.

    Intenta reutilizar una wallet expirada antes de crear una nueva.

    Args:
        request: Solicitud para crear wallet
        current_user: Usuario autenticado
        wallet_service: Servicio de Wallet
        pool_service: Servicio de Pool

    Returns:
        WalletResponse: Wallet creada/asignada

    Raises:
        HTTPException: 400 si hay error en la creación
    """
    # Intentar obtener wallet del pool
    bsx_wallet = await pool_service.get_or_assign_wallet(
        user_id=current_user.id,
        telegram_id=current_user.telegram_id,
        label=request.label,
    )

    if not bsx_wallet:
        raise HTTPException(status_code=400, detail="Failed to assign wallet")

    # Obtener la wallet desde el repositorio
    wallet = await wallet_service.get_wallet(current_user.id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet created but not found")

    return wallet


@router.patch(
    "/{wallet_id}",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
)
async def update_wallet(
    wallet_id: UUID,
    request: WalletUpdateRequest,
    current_user: User = Depends(get_current_user),
    wallet_service: WalletManagementService = Depends(get_wallet_management_service),
):
    """
    Actualiza una wallet existente.

    Args:
        wallet_id: UUID de la wallet
        request: Solicitud de actualización
        current_user: Usuario autenticado
        wallet_service: Servicio de Wallet

    Returns:
        WalletResponse: Wallet actualizada

    Raises:
        HTTPException: 404 si no existe, 403 si no está autorizado
    """
    wallet = await wallet_service.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Verificar autorización
    if wallet.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this wallet")

    # Actualizar campos
    if request.label is not None:
        wallet.label = request.label
    if request.status is not None:
        if request.status.value == "active":
            await wallet_service.activate_wallet(wallet_id)
        elif request.status.value == "inactive":
            await wallet_service.deactivate_wallet(wallet_id)
        wallet.status = request.status

    updated_wallet = await wallet_service.update_balance(
        wallet_id, 0
    )  # Solo para obtener la wallet actualizada
    if not updated_wallet:
        raise HTTPException(status_code=404, detail="Failed to update wallet")

    return updated_wallet


@router.post(
    "/{wallet_id}/deposit",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
)
async def deposit_to_wallet(
    wallet_id: UUID,
    request: WalletDepositRequest,
    current_user: User = Depends(get_current_user),
    wallet_service: WalletManagementService = Depends(get_wallet_management_service),
):
    """
    Deposita fondos en una wallet.

    Args:
        wallet_id: UUID de la wallet
        request: Monto a depositar
        current_user: Usuario autenticado
        wallet_service: Servicio de Wallet

    Returns:
        WalletResponse: Wallet actualizada

    Raises:
        HTTPException: 404 si no existe, 403 si no está autorizado
    """
    wallet = await wallet_service.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Verificar autorización
    if wallet.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to deposit to this wallet")

    updated_wallet = await wallet_service.update_balance(wallet_id, request.amount_usdt)
    if not updated_wallet:
        raise HTTPException(status_code=400, detail="Failed to deposit")

    return updated_wallet


@router.post(
    "/{wallet_id}/withdraw",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
)
async def withdraw_from_wallet(
    wallet_id: UUID,
    request: WalletWithdrawRequest,
    current_user: User = Depends(get_current_user),
    wallet_service: WalletManagementService = Depends(get_wallet_management_service),
):
    """
    Retira fondos de una wallet.

    Args:
        wallet_id: UUID de la wallet
        request: Monto a retirar
        current_user: Usuario autenticado
        wallet_service: Servicio de Wallet

    Returns:
        WalletResponse: Wallet actualizada

    Raises:
        HTTPException: 404 si no existe, 403 si no está autorizado, 400 si fondos insuficientes
    """
    wallet = await wallet_service.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Verificar autorización
    if wallet.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to withdraw from this wallet")

    # Verificar fondos suficientes
    if wallet.balance_usdt < request.amount_usdt:
        raise HTTPException(
            status_code=400, detail=f"Insufficient balance. Available: {wallet.balance_usdt} USDT"
        )

    updated_wallet = await wallet_service.update_balance(wallet_id, -request.amount_usdt)
    if not updated_wallet:
        raise HTTPException(status_code=400, detail="Failed to withdraw")

    return updated_wallet


@router.get(
    "/pool/stats",
    response_model=WalletPoolStats,
    status_code=status.HTTP_200_OK,
)
async def get_pool_stats(
    current_user: User = Depends(get_current_user),
    pool_service: WalletPoolService = Depends(get_wallet_pool_service),
):
    """
    Obtiene estadísticas del pool de wallets.

    Solo disponible para administradores.

    Args:
        current_user: Usuario autenticado
        pool_service: Servicio de Pool

    Returns:
        WalletPoolStats: Estadísticas del pool

    Raises:
        HTTPException: 403 si no es administrador
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    stats = await pool_service.get_pool_stats()
    return WalletPoolStats(**stats)


@router.get(
    "/pool",
    response_model=list[WalletPoolResponse],
    status_code=status.HTTP_200_OK,
)
async def get_pool_wallets(
    current_user: User = Depends(get_current_user),
    pool_service: WalletPoolService = Depends(get_wallet_pool_service),
):
    """
    Obtiene todas las wallets del pool.

    Solo disponible para administradores.

    Args:
        current_user: Usuario autenticado
        pool_service: Servicio de Pool

    Returns:
        List[WalletPoolResponse]: Lista de wallets del pool

    Raises:
        HTTPException: 403 si no es administrador
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    wallets = await pool_service.wallet_pool_repo.get_all()
    return [WalletPoolResponse.model_validate(w) for w in wallets]
