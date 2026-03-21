"""Schemas compartidos."""

from .admin import (
    AdminKeyInfoResponse,
    AdminKeyListResponse,
    AdminOperationResultResponse,
    AdminUserInfoResponse,
    AdminUserListResponse,
    AssignRoleRequest,
    DashboardStatsResponse,
    DeleteKeyResponse,
    ServerStatsResponse,
    ServerStatusListResponse,
    ServerStatusResponse,
    ToggleKeyStatusRequest,
    UpdateUserStatusRequest,
)
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
from .wallet import (
    WalletCreateRequest,
    WalletDepositRequest,
    WalletPoolResponse,
    WalletPoolStats,
    WalletResponse,
    WalletUpdateRequest,
    WalletWithdrawRequest,
)

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
    # Wallet schemas
    "WalletResponse",
    "WalletCreateRequest",
    "WalletUpdateRequest",
    "WalletDepositRequest",
    "WalletWithdrawRequest",
    "WalletPoolResponse",
    "WalletPoolStats",
    # Admin schemas
    "AdminUserInfoResponse",
    "AdminUserListResponse",
    "AdminKeyInfoResponse",
    "AdminKeyListResponse",
    "ServerStatusResponse",
    "ServerStatusListResponse",
    "ServerStatsResponse",
    "DashboardStatsResponse",
    "AdminOperationResultResponse",
    "UpdateUserStatusRequest",
    "AssignRoleRequest",
    "ToggleKeyStatusRequest",
    "DeleteKeyResponse",
]
