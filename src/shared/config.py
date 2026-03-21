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

    # ==================================================================
    # APPLICATION SETTINGS
    # ==================================================================
    APP_ENV: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "uSipipo Backend"
    DEFAULT_LANG: str = "es"
    API_PREFIX: str = "/api/v1"

    # ==================================================================
    # SECURITY CONFIGURATION
    # ==================================================================
    SECRET_KEY: str = "change_me_in_production_use_openssl_rand_hex_32"
    JWT_SECRET: str = "change_me_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_EXPIRATION_HOURS: int = 24

    # ==================================================================
    # TELEGRAM BOT CONFIGURATION
    # ==================================================================
    TELEGRAM_TOKEN: str = ""
    BOT_USERNAME: str = "usipipo_bot"
    ADMIN_ID: int = 0
    AUTHORIZED_USERS: list[int] = []
    TELEGRAM_RATE_LIMIT: int = 30
    TELEGRAM_STARS_TO_USD: float = 0.02  # 1 Star ≈ $0.02 USD

    # ==================================================================
    # SERVER CONFIGURATION
    # ==================================================================
    SERVER_IP: str = "127.0.0.1"
    SERVER_IPV4: str = "127.0.0.1"

    # ==================================================================
    # API CONFIGURATION
    # ==================================================================
    API_HOST: str = "0.0.0.0"  # nosec B104 - Required for Docker/production
    API_PORT: int = 8000
    API_RATE_LIMIT: int = 60
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # ==================================================================
    # DATABASE CONFIGURATION
    # ==================================================================
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/usipipo"
    DB_POOL_SIZE: int = 10
    DB_TIMEOUT: int = 30

    # ==================================================================
    # REDIS CONFIGURATION
    # ==================================================================
    REDIS_URL: str = "redis://localhost:6379"

    # ==================================================================
    # MINI APP CONFIGURATION
    # ==================================================================
    MINIAPP_ENABLED: bool = True
    MINIAPP_URL: str = "https://localhost"

    # ==================================================================
    # WIREGUARD VPN CONFIGURATION
    # ==================================================================
    WG_INTERFACE: str = "wg0"
    WG_SERVER_PORT: int = 51820
    WG_SERVER_PUBKEY: str = ""
    WG_SERVER_PRIVKEY: str = ""
    WG_PATH: str = "/etc/wireguard"
    WG_ENDPOINT: str = ""
    WG_CLIENT_DNS_1: str = "1.1.1.1"
    WG_CLIENT_DNS_2: str = "1.0.0.1"
    WG_SERVER_IPV4: str = ""
    WG_SERVER_IPV6: str = ""
    WG_ALLOWED_IPS: str = ""

    # ==================================================================
    # OUTLINE VPN CONFIGURATION
    # ==================================================================
    OUTLINE_API_URL: str = ""
    OUTLINE_VERIFY_SSL: bool = False
    OUTLINE_API_PORT: str = ""
    OUTLINE_KEYS_PORT: str = ""
    OUTLINE_SERVER_IP: str = ""
    OUTLINE_DASHBOARD_URL: str = ""
    OUTLINE_CERT_SHA256: str = ""

    # ==================================================================
    # VPN KEY LIMITS
    # ==================================================================
    VPN_KEY_EXPIRE_DAYS: int = 30
    MAX_KEYS_PER_USER: int = 5

    # ==================================================================
    # PLAN CONFIGURATION
    # ==================================================================
    FREE_PLAN_MAX_KEYS: int = 2
    FREE_PLAN_DATA_LIMIT_GB: int = 10
    VIP_PLAN_MAX_KEYS: int = 10
    VIP_PLAN_DATA_LIMIT_GB: int = 50
    VIP_PLAN_COST_STARS: int = 10
    BILLING_CYCLE_DAYS: int = 30
    KEY_CLEANUP_DAYS: int = 90
    REFERRAL_COMMISSION_PERCENT: int = 10

    # ==================================================================
    # LOGGING & MONITORING
    # ==================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "./logs/backend.log"
    ENABLE_METRICS: bool = False

    # ==================================================================
    # AUTO MEMORY CLEANUP (RAM)
    # ==================================================================
    MEMORY_CLEANUP_ENABLED: bool = True
    MEMORY_CLEANUP_THRESHOLD_PERCENT: int = 80
    MEMORY_CLEANUP_CRITICAL_PERCENT: int = 90
    MEMORY_CLEANUP_INTERVAL_MINUTES: int = 10
    MEMORY_NOTIFY_ADMIN: bool = True

    # ==================================================================
    # PATHS & DIRECTORIES
    # ==================================================================
    TEMP_PATH: str = "./temp"
    QR_CODE_PATH: str = "./static/qr_codes"
    CLIENT_CONFIGS_PATH: str = "./static/configs"

    # ==================================================================
    # PAYMENT - TRON DEALER API (Crypto Payments)
    # ==================================================================
    TRON_DEALER_API_KEY: str = ""
    TRON_DEALER_WEBHOOK_SECRET: str = ""
    TRON_DEALER_SWEEP_WALLET: str = ""

    # ==================================================================
    # DYNAMIC DNS (DuckDNS)
    # ==================================================================
    DUCKDNS_DOMAIN: str = ""
    DUCKDNS_TOKEN: str = ""
    PUBLIC_URL: str = "https://localhost"

    # ==================================================================
    # CONSUMPTION BILLING (Pay-as-you-go)
    # ==================================================================
    CONSUMPTION_PRICE_PER_GB_USD: float = 0.25
    CONSUMPTION_PRICE_PER_MB_USD: float = 0.000244140625  # 0.25 / 1024
    CONSUMPTION_CYCLE_DAYS: int = 30
    CONSUMPTION_INVOICE_EXPIRY_MINUTES: int = 30

    # ==================================================================
    # REFERRAL SYSTEM
    # ==================================================================
    REFERRAL_CREDITS_PER_REFERRAL: int = 100
    REFERRAL_BONUS_NEW_USER: int = 50
    REFERRAL_CREDITS_PER_GB: int = 100

    # ==================================================================
    # HELPER PROPERTIES
    # ==================================================================
    @property
    def is_development(self) -> bool:
        """Verifica si la aplicación está en modo desarrollo."""
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        """Verifica si la aplicación está en modo producción."""
        return self.APP_ENV == "production"

    @property
    def webhook_url(self) -> str:
        """Obtiene la URL del webhook para Telegram."""
        return f"{self.PUBLIC_URL}/api/v1/webhooks/telegram/{self.TELEGRAM_TOKEN}"


@lru_cache
def get_settings() -> Settings:
    """
    Obtiene la configuración de la aplicación (cached).

    Returns:
        Settings: Configuración cargada
    """
    return Settings()


settings = get_settings()
