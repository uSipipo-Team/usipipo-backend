"""Configuración de la aplicación usando pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    TELEGRAM_STARS_TO_USD: float = 0.02  # 1 Star ≈ $0.02 USD

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/usipipo"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Payment - TronDealer
    TRON_DEALER_API_KEY: str = ""
    TRON_DEALER_WEBHOOK_SECRET: str = ""

    # VPN - Outline
    OUTLINE_API_URL: str = ""
    OUTLINE_VERIFY_SSL: bool = False
    OUTLINE_API_PORT: str = ""
    OUTLINE_KEYS_PORT: str = ""
    OUTLINE_SERVER_IP: str = ""
    OUTLINE_DASHBOARD_URL: str = ""
    OUTLINE_CERT_SHA256: str = ""

    # VPN - WireGuard
    WG_INTERFACE: str = "wg0"
    WG_PATH: str = "/etc/wireguard"
    WG_SERVER_PORT: int = 51820
    SERVER_IP: str = ""
    WG_CLIENT_DNS_1: str = "1.1.1.1"
    WG_CLIENT_DNS_2: str = "1.0.0.1"
    WG_SERVER_IPV4: str = ""
    WG_SERVER_IPV6: str = ""
    WG_SERVER_PUBKEY: str = ""
    WG_SERVER_PRIVKEY: str = ""
    WG_ALLOWED_IPS: str = ""
    WG_ENDPOINT: str = ""

    # ==================================================================
    # SISTEMA DE TARIFA POR CONSUMO (PAY-AS-YOU-GO)
    # ==================================================================
    CONSUMPTION_PRICE_PER_GB_USD: float = 0.25
    CONSUMPTION_PRICE_PER_MB_USD: float = 0.000244140625  # 0.25 / 1024
    CONSUMPTION_CYCLE_DAYS: int = 30
    CONSUMPTION_INVOICE_EXPIRY_MINUTES: int = 30

    # ==================================================================
    # SISTEMA DE REFERIDOS
    # ==================================================================
    REFERRAL_CREDITS_PER_REFERRAL: int = 100
    REFERRAL_BONUS_NEW_USER: int = 50
    REFERRAL_CREDITS_PER_GB: int = 100

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
