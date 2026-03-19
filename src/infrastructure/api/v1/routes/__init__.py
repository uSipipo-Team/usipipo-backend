"""Routes de API v1."""

from .auth import router as auth_router
from .vpn import router as vpn_router

__all__ = ["auth_router", "vpn_router"]
