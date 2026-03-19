"""Seguridad JWT para autenticación."""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from ...shared.config import settings


def create_jwt_token(
    user_id: UUID,
    telegram_id: int,
    expires_delta: Optional[timedelta] = None,
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
    now = datetime.now(timezone.utc)
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
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


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
