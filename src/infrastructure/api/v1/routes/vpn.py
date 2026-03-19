"""Routes para gestión de claves VPN."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from usipipo_commons.domain.entities.user import User

from src.core.application.services.vpn_service import VpnService
from src.infrastructure.api.v1.deps import get_current_user, get_vpn_service
from src.shared.schemas.vpn import (
    CreateVpnKeyRequest,
    UpdateVpnKeyRequest,
    VpnKeyResponse,
)

router = APIRouter(prefix="/vpn", tags=["VPN Keys"])


@router.get(
    "/keys",
    response_model=list[VpnKeyResponse],
    status_code=status.HTTP_200_OK,
)
async def list_vpn_keys(
    current_user: User = Depends(get_current_user),
    vpn_service: VpnService = Depends(get_vpn_service),
):
    """
    Lista todas las claves VPN del usuario.

    Args:
        current_user: Usuario autenticado
        vpn_service: Servicio de VPN

    Returns:
        List[VpnKeyResponse]: Lista de claves VPN
    """
    keys = await vpn_service.get_user_keys(current_user.id)
    return keys


@router.post(
    "/keys",
    response_model=VpnKeyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_vpn_key(
    request: CreateVpnKeyRequest,
    current_user: User = Depends(get_current_user),
    vpn_service: VpnService = Depends(get_vpn_service),
):
    """
    Crea una nueva clave VPN.

    Args:
        request: Solicitud para crear clave VPN
        current_user: Usuario autenticado
        vpn_service: Servicio de VPN

    Returns:
        VpnKeyResponse: Clave VPN creada

    Raises:
        HTTPException: 400 si hay error en la creación
    """
    try:
        key = await vpn_service.create_key(
            user_id=current_user.id,
            name=request.name,
            vpn_type=request.vpn_type.value,
            data_limit_gb=request.data_limit_gb,
        )
        return key
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create key: {str(e)}",
        )


@router.get(
    "/keys/{key_id}",
    response_model=VpnKeyResponse,
    status_code=status.HTTP_200_OK,
)
async def get_vpn_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    vpn_service: VpnService = Depends(get_vpn_service),
):
    """
    Obtiene detalles de una clave VPN.

    Args:
        key_id: UUID de la clave
        current_user: Usuario autenticado
        vpn_service: Servicio de VPN

    Returns:
        VpnKeyResponse: Detalles de la clave

    Raises:
        HTTPException: 404 si no existe, 403 si no está autorizado
    """
    key = await vpn_service.get_key_by_id(key_id)

    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key not found",
        )

    if key.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this key",
        )

    return key


@router.delete(
    "/keys/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_vpn_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    vpn_service: VpnService = Depends(get_vpn_service),
):
    """
    Elimina una clave VPN.

    Args:
        key_id: UUID de la clave
        current_user: Usuario autenticado
        vpn_service: Servicio de VPN

    Raises:
        HTTPException: 404 si no existe, 403 si no está autorizado
    """
    try:
        await vpn_service.delete_key(current_user.id, key_id)
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this key",
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete key: {str(e)}",
        )


@router.put(
    "/keys/{key_id}",
    response_model=VpnKeyResponse,
    status_code=status.HTTP_200_OK,
)
async def update_vpn_key(
    key_id: UUID,
    request: UpdateVpnKeyRequest,
    current_user: User = Depends(get_current_user),
    vpn_service: VpnService = Depends(get_vpn_service),
):
    """
    Actualiza una clave VPN.

    Args:
        key_id: UUID de la clave
        request: Solicitud de actualización
        current_user: Usuario autenticado
        vpn_service: Servicio de VPN

    Returns:
        VpnKeyResponse: Clave VPN actualizada

    Raises:
        HTTPException: 404 si no existe, 403 si no está autorizado
    """
    try:
        key = await vpn_service.update_key(
            user_id=current_user.id,
            key_id=key_id,
            name=request.name,
            data_limit_gb=request.data_limit_gb,
        )
        return key
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this key",
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update key: {str(e)}",
        )
