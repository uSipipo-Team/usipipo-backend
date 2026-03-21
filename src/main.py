"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .infrastructure.api.v1.routes.admin import router as admin_router
from .infrastructure.api.v1.routes.auth import router as auth_router
from .infrastructure.api.v1.routes.billing import router as billing_router
from .infrastructure.api.v1.routes.consumption_invoices import (
    router as consumption_invoices_router,
)
from .infrastructure.api.v1.routes.payments import router as payments_router
from .infrastructure.api.v1.routes.subscriptions import router as subscriptions_router
from .infrastructure.api.v1.routes.tickets import router as tickets_router
from .infrastructure.api.v1.routes.vpn import router as vpn_router
from .infrastructure.api.v1.webhooks.crypto import router as crypto_webhook_router
from .infrastructure.api.v1.webhooks.telegram_stars import router as telegram_stars_webhook_router
from .infrastructure.persistence.database import close_db, init_db
from .shared.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.

    Args:
        app: Instancia de FastAPI
    """
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="uSipipo Backend API",
    description="Backend API principal del ecosistema uSipipo",
    version="0.1.0",
    lifespan=lifespan,
)


# Incluir routers de API v1
api_prefix = f"{settings.API_PREFIX}"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(vpn_router, prefix=api_prefix)
app.include_router(payments_router, prefix=api_prefix)
app.include_router(billing_router, prefix=api_prefix)
app.include_router(subscriptions_router, prefix=api_prefix)
app.include_router(consumption_invoices_router, prefix=api_prefix)
app.include_router(tickets_router, prefix=api_prefix)
app.include_router(admin_router, prefix=api_prefix)

# Incluir webhooks (sin prefijo de API)
app.include_router(crypto_webhook_router, prefix=api_prefix)
app.include_router(telegram_stars_webhook_router, prefix=api_prefix)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to uSipipo Backend API",
        "docs": "/docs",
        "health": "/health",
    }
