"""Consumption invoice schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ConsumptionInvoiceResponse(BaseModel):
    """Response schema for consumption invoice."""

    id: uuid.UUID
    billing_id: uuid.UUID
    user_id: int
    amount_usd: Decimal
    wallet_address: str
    payment_method: str
    status: str
    expires_at: datetime
    paid_at: datetime | None = None
    transaction_hash: str | None = None
    telegram_payment_id: str | None = None
    created_at: datetime
    time_remaining_seconds: int | None = None
    is_expired: bool | None = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class ConsumptionInvoiceCreateRequest(BaseModel):
    """Request schema for creating a consumption invoice."""

    billing_id: uuid.UUID
    user_id: int
    amount_usd: Decimal = Field(ge=0, description="Amount in USD")
    payment_method: str = Field(default="crypto", description="Payment method: crypto or stars")


class ConsumptionInvoicePaymentRequest(BaseModel):
    """Request schema for marking an invoice as paid."""

    transaction_hash: str | None = Field(default=None, description="Crypto transaction hash")
    telegram_payment_id: str | None = Field(default=None, description="Telegram payment ID")


class ConsumptionInvoiceStatusUpdateRequest(BaseModel):
    """Request schema for updating invoice status."""

    status: str = Field(description="New status: pending, paid, or expired")


class ConsumptionInvoiceListResponse(BaseModel):
    """Response schema for list of invoices."""

    invoices: list[ConsumptionInvoiceResponse]
    total: int = Field(ge=0)
    pending_count: int = Field(ge=0)
    paid_count: int = Field(ge=0)
    expired_count: int = Field(ge=0)
