"""Schemas para autenticación."""

from pydantic import BaseModel, Field


class TelegramAuthRequest(BaseModel):
    """Solicitud de autenticación con Telegram."""

    init_data: str = Field(..., description="Telegram WebApp initData")


class AuthResponse(BaseModel):
    """Respuesta de autenticación."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 horas
    user_id: str
