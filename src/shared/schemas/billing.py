"""Billing schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UsageResponse(BaseModel):
    """Usage response schema."""

    balance_gb: float = Field(ge=0)
    total_purchased_gb: float = Field(ge=0)
    keys_count: int = Field(ge=0)
    data_used_gb: float = Field(ge=0)
    data_limit_gb: float = Field(ge=0)
    usage_percentage: float = Field(ge=0, le=100)


class KeyUsageResponse(BaseModel):
    """Key usage response schema."""

    key_id: UUID
    name: str
    data_used_gb: float
    data_limit_gb: float
    usage_percentage: float
    expires_at: datetime | None = None
