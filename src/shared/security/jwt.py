"""Seguridad JWT para autenticación."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from ...shared.config import settings


def create_jwt_token(
    user_id: UUID,
    telegram_id: int,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Crea JWT token para usuario.

    Args:
        user_id: UUID del usuario
        telegram_id: ID de Telegram del usuario
        expires_delta: Tiempo de expiración opcional

    Returns:
        str: JWT token encoded
    """
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(hours=settings.JWT_EXPIRATION_HOURS))

    payload = {
        "sub": str(user_id),
        "telegram_id": telegram_id,
        "exp": expire,
        "iat": now,
        "type": "access",
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_jwt_token(token: str) -> dict:
    """
    Decodifica y valida JWT token.

    Args:
        token: JWT token a decodificar

    Returns:
        dict: Payload del token

    Raises:
        ValueError: Si el token es inválido o expiró
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired") from None
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token") from None


def verify_jwt_token(token: str) -> bool:
    """
    Verifica si un token es válido sin decodificarlo.

    Args:
        token: JWT token a verificar

    Returns:
        bool: True si es válido, False si no
    """
    try:
        decode_jwt_token(token)
        return True
    except ValueError:
        return False
