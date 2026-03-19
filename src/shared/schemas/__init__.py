"""Schemas compartidos."""

from .auth import AuthResponse, TelegramAuthRequest
from .vpn import CreateVpnKeyRequest, UpdateVpnKeyRequest, VpnKeyResponse

__all__ = [
    "TelegramAuthRequest",
    "AuthResponse",
    "VpnKeyResponse",
    "CreateVpnKeyRequest",
    "UpdateVpnKeyRequest",
]
