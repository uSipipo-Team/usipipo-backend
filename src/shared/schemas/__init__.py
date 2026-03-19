"""Schemas compartidos."""

from .auth import TelegramAuthRequest, AuthResponse
from .vpn import VpnKeyResponse, CreateVpnKeyRequest, UpdateVpnKeyRequest

__all__ = [
    "TelegramAuthRequest",
    "AuthResponse",
    "VpnKeyResponse",
    "CreateVpnKeyRequest",
    "UpdateVpnKeyRequest",
]
