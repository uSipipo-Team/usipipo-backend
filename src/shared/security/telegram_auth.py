"""Autenticación con Telegram WebApp."""

import hashlib
import hmac
import json
from typing import Dict, Optional
from urllib.parse import parse_qs

from ...shared.config import settings


def validate_telegram_init_data(init_data: str) -> Optional[Dict[str, str]]:
    """
    Valida initData de Telegram WebApp.

    Args:
        init_data: El initData recibido de Telegram WebApp

    Returns:
        Dict con los datos parseados si es válido, None si es inválido
    """
    try:
        # Parsear query string
        parsed = parse_qs(init_data)
        data = {k: v[0] for k, v in parsed.items()}

        # Extraer hash
        received_hash = data.pop("hash", None)
        if not received_hash:
            return None

        # Ordenar datos para hashing
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(data.items())
        )

        # Crear secret key desde BOT_TOKEN
        secret_key = hmac.new(
            b"WebAppData",
            settings.TELEGRAM_TOKEN.encode(),
            hashlib.sha256,
        ).digest()

        # Calcular hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Verificar
        if not hmac.compare_digest(calculated_hash, received_hash):
            return None

        return data

    except Exception:
        return None


def extract_user_from_telegram_data(data: Dict[str, str]) -> dict:
    """
    Extrae información del usuario desde Telegram initData.

    Args:
        data: Datos validados de Telegram

    Returns:
        Dict con información del usuario
    """
    user_json = data.get("user", "{}")
    user = json.loads(user_json)

    return {
        "telegram_id": int(user["id"]),
        "username": user.get("username"),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "language_code": user.get("language_code"),
        "is_premium": user.get("is_premium", False),
    }


def is_telegram_init_data_valid(init_data: str) -> bool:
    """
    Verifica si el initData de Telegram es válido.

    Args:
        init_data: El initData recibido de Telegram WebApp

    Returns:
        bool: True si es válido, False si no
    """
    return validate_telegram_init_data(init_data) is not None
