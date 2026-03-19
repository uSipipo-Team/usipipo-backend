"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from .infrastructure.persistence.database import init_db, close_db
from .infrastructure.api.v1.routes.auth import router as auth_router
from .infrastructure.api.v1.routes.vpn import router as vpn_router
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
