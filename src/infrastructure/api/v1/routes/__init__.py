"""Routes de API v1."""

from .admin import router as admin_router
from .auth import router as auth_router
from .billing import router as billing_router
from .consumption_invoices import router as consumption_invoices_router
from .payments import router as payments_router
from .subscriptions import router as subscriptions_router
from .tickets import router as tickets_router
from .vpn import router as vpn_router

__all__ = [
    "auth_router",
    "vpn_router",
    "payments_router",
    "billing_router",
    "subscriptions_router",
    "consumption_invoices_router",
    "tickets_router",
    "admin_router",
]
