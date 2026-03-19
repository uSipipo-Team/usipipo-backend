"""Routes de autenticación."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.application.services.user_service import UserService
from src.infrastructure.api.v1.deps import get_user_service
from src.shared.schemas.auth import AuthResponse, TelegramAuthRequest
from src.shared.security.jwt import create_jwt_token
from src.shared.security.telegram_auth import (
    extract_user_from_telegram_data,
    validate_telegram_init_data,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/telegram",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
async def authenticate_telegram(
    request: TelegramAuthRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Autentica usuario con Telegram WebApp initData.

    Valida el initData de Telegram y retorna JWT token.

    Args:
        request: Solicitud con initData de Telegram
        user_service: Servicio de usuarios

    Returns:
        AuthResponse: Token JWT y datos de autenticación

    Raises:
        HTTPException: 401 si el initData es inválido
    """
    # Validar initData
    telegram_data = validate_telegram_init_data(request.init_data)
    if not telegram_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram initData",
        )

    # Extraer datos del usuario
    user_info = extract_user_from_telegram_data(telegram_data)

    # Buscar o crear usuario
    user = await user_service.get_or_create_by_telegram(
        telegram_id=user_info["telegram_id"],
        username=user_info.get("username"),
        first_name=user_info.get("first_name"),
        last_name=user_info.get("last_name"),
    )

    # Generar JWT
    access_token = create_jwt_token(user.id, user.telegram_id)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400,  # 24 horas
        user_id=str(user.id),
    )
