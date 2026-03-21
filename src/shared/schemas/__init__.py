"""Schemas compartidos."""

from .auth import AuthResponse, TelegramAuthRequest
from .billing import KeyUsageResponse, UsageResponse
from .consumption_invoice import (
    ConsumptionInvoiceCreateRequest,
    ConsumptionInvoiceListResponse,
    ConsumptionInvoicePaymentRequest,
    ConsumptionInvoiceResponse,
    ConsumptionInvoiceStatusUpdateRequest,
)
from .vpn import CreateVpnKeyRequest, UpdateVpnKeyRequest, VpnKeyResponse

__all__ = [
    "TelegramAuthRequest",
    "AuthResponse",
    "VpnKeyResponse",
    "CreateVpnKeyRequest",
    "UpdateVpnKeyRequest",
    "UsageResponse",
    "KeyUsageResponse",
    "ConsumptionInvoiceResponse",
    "ConsumptionInvoiceCreateRequest",
    "ConsumptionInvoicePaymentRequest",
    "ConsumptionInvoiceStatusUpdateRequest",
    "ConsumptionInvoiceListResponse",
]
