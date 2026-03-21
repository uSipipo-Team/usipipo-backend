"""Entry point for running the backend service."""

import os

import uvicorn

from src.shared.config import settings


def main():
    """Run the backend service using configuration from .env."""
    # Get configuration from environment variables
    host = os.getenv("API_HOST", settings.API_HOST)
    port = int(os.getenv("API_PORT", settings.API_PORT))
    workers = int(os.getenv("UVICORN_WORKERS", 4))
    reload = os.getenv("DEBUG", "false").lower() == "true"

    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        workers=workers,
        reload=reload,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )


if __name__ == "__main__":
    main()
