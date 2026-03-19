"""Configuración de la aplicación usando pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # Security
    JWT_SECRET: str = "change_me_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Telegram
    TELEGRAM_TOKEN: str = ""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/usipipo"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    @property
    def is_development(self) -> bool:
        """Verifica si la aplicación está en modo desarrollo."""
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        """Verifica si la aplicación está en modo producción."""
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Obtiene la configuración de la aplicación (cached).

    Returns:
        Settings: Configuración cargada
    """
    return Settings()


settings = get_settings()
