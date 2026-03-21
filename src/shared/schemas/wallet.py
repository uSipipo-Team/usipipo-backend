"""Schemas para Wallet."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from usipipo_commons.domain.enums.wallet_status import WalletStatus


class WalletResponse(BaseModel):
    """Respuesta de wallet."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    address: str
    label: str | None = None
    status: WalletStatus
    balance_usdt: float = 0.0
    created_at: datetime
    updated_at: datetime
    last_used_at: datetime | None = None
    total_received_usdt: float = 0.0
    transaction_count: int = 0


class WalletCreateRequest(BaseModel):
    """Solicitud para crear wallet."""

    label: str | None = Field(
        None, min_length=1, max_length=100, description="Label opcional para la wallet"
    )


class WalletUpdateRequest(BaseModel):
    """Solicitud para actualizar wallet."""

    label: str | None = Field(None, min_length=1, max_length=100)
    status: WalletStatus | None = None


class WalletDepositRequest(BaseModel):
    """Solicitud para depositar en wallet."""

    amount_usdt: float = Field(..., gt=0, description="Monto a depositar en USDT")


class WalletWithdrawRequest(BaseModel):
    """Solicitud para retirar de wallet."""

    amount_usdt: float = Field(..., gt=0, description="Monto a retirar en USDT")


class WalletPoolResponse(BaseModel):
    """Respuesta de entrada de pool de wallet."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    wallet_address: str
    original_user_id: UUID | None = None
    status: WalletStatus
    created_at: datetime
    released_at: datetime
    expires_at: datetime
    reused_by_user_id: UUID | None = None
    reused_at: datetime | None = None


class WalletPoolStats(BaseModel):
    """Estadísticas del pool de wallets."""

    total: int
    available: int
    expired: int
    in_use: int
