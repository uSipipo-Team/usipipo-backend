"""Payment schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from usipipo_commons.domain.enums import PaymentMethod, PaymentStatus


class PaymentResponse(BaseModel):
    """Payment response schema."""

    id: UUID
    user_id: UUID
    amount_usd: float
    gb_purchased: float
    method: PaymentMethod
    status: PaymentStatus
    crypto_address: str | None = None
    crypto_network: str | None = None
    telegram_star_invoice_id: str | None = None
    created_at: datetime
    expires_at: datetime | None = None
    paid_at: datetime | None = None
    transaction_hash: str | None = None

    class Config:
        from_attributes = True


class CreateCryptoPaymentRequest(BaseModel):
    """Request schema for creating crypto payment."""

    amount_usd: float = Field(..., gt=0, description="Amount in USD")
    gb_purchased: float = Field(..., gt=0, description="GB to purchase")
    network: str = Field(default="BSC", description="Network: BSC or TRC20")


class CreateTelegramStarsPaymentRequest(BaseModel):
    """Request schema for creating Telegram Stars payment."""

    amount_usd: float = Field(..., gt=0, description="Amount in USD")
    gb_purchased: float = Field(..., gt=0, description="GB to purchase")
