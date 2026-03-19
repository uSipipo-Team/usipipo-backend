"""Dependencias para autenticación y autorización."""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.user import User

from src.core.application.services.user_service import UserService
from src.core.application.services.vpn_service import VpnService
from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.repositories.vpn_repository import VpnRepository
from src.shared.security.jwt import decode_jwt_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Obtiene usuario actual desde JWT token.

    Args:
        credentials: Credenciales HTTP Bearer
        db: Sesión de base de datos

    Returns:
        User: Usuario autenticado

    Raises:
        HTTPException: 401 si el token es inválido o expiró
    """
    token = credentials.credentials

    try:
        payload = decode_jwt_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = UUID(payload["sub"])

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Requiere que el usuario sea admin.

    Args:
        current_user: Usuario actual

    Returns:
        User: Usuario admin

    Raises:
        HTTPException: 403 si el usuario no es admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


async def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    """
    Dependency para obtener UserService.

    Args:
        db: Sesión de base de datos

    Returns:
        UserService: Servicio de usuarios
    """
    user_repo = UserRepository(db)
    return UserService(user_repo)


async def get_vpn_service(
    db: AsyncSession = Depends(get_db),
) -> VpnService:
    """
    Dependency para obtener VpnService.

    Args:
        db: Sesión de base de datos

    Returns:
        VpnService: Servicio de VPN
    """
    user_repo = UserRepository(db)
    vpn_repo = VpnRepository(db)
    return VpnService(user_repo, vpn_repo)
