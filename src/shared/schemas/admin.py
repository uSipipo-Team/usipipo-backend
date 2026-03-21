"""Pydantic schemas for admin API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# ============================================
# Admin User Schemas
# ============================================


class AdminUserInfoResponse(BaseModel):
    """Response schema for admin user information."""

    user_id: int = Field(..., description="Telegram user ID")
    username: str | None = Field(None, description="Username")
    first_name: str = Field(..., description="First name")
    last_name: str | None = Field(None, description="Last name")
    total_keys: int = Field(..., description="Total number of VPN keys")
    active_keys: int = Field(..., description="Number of active VPN keys")
    stars_balance: int = Field(0, description="Balance in stars (deprecated)")
    total_deposited: int = Field(0, description="Total deposited amount")
    referral_credits: int = Field(0, description="Referral credits")
    registration_date: datetime | None = Field(None, description="Registration date")
    last_activity: datetime | None = Field(None, description="Last activity date")

    model_config = {"from_attributes": True}


class AdminUserListResponse(BaseModel):
    """Response schema for list of users."""

    users: list[AdminUserInfoResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class AdminUserDetailResponse(BaseModel):
    """Response schema for detailed user information."""

    user_id: int = Field(..., description="Telegram user ID")
    username: str | None = Field(None, description="Username")
    full_name: str = Field(..., description="Full name")
    status: str = Field(..., description="User status")
    role: str = Field(..., description="User role")
    total_keys: int = Field(..., description="Total number of VPN keys")
    active_keys: int = Field(..., description="Number of active VPN keys")
    balance_stars: int = Field(0, description="Balance in stars")
    total_deposited: int = Field(0, description="Total deposited amount")
    referral_credits: int = Field(0, description="Referral credits")
    created_at: datetime = Field(..., description="Creation date")


# ============================================
# Admin Key Schemas
# ============================================


class AdminKeyInfoResponse(BaseModel):
    """Response schema for admin key information."""

    key_id: str = Field(..., description="Key ID")
    user_id: int = Field(..., description="Telegram user ID")
    user_name: str = Field(..., description="User name")
    key_type: str = Field(..., description="Key type (wireguard, outline)")
    key_name: str = Field(..., description="Key name")
    access_url: str | None = Field(None, description="Access URL")
    created_at: datetime = Field(..., description="Creation date")
    last_used: datetime | None = Field(None, description="Last used date")
    data_limit: int = Field(..., description="Data limit in bytes")
    data_used: int = Field(..., description="Data used in bytes")
    is_active: bool = Field(..., description="Whether key is active")
    server_status: str = Field(..., description="Server status")

    model_config = {"from_attributes": True}


class AdminKeyListResponse(BaseModel):
    """Response schema for list of keys."""

    keys: list[AdminKeyInfoResponse] = Field(..., description="List of keys")
    total: int = Field(..., description="Total number of keys")


# ============================================
# Admin Server Schemas
# ============================================


class ServerStatusResponse(BaseModel):
    """Response schema for server status."""

    server_type: str = Field(..., description="Server type")
    is_healthy: bool = Field(..., description="Whether server is healthy")
    total_keys: int = Field(..., description="Total keys on server")
    active_keys: int = Field(..., description="Active keys on server")
    version: str | None = Field(None, description="Server version")
    uptime: str | None = Field(None, description="Server uptime")
    error_message: str | None = Field(None, description="Error message if any")

    model_config = {"from_attributes": True}


class ServerStatusListResponse(BaseModel):
    """Response schema for list of server statuses."""

    wireguard: ServerStatusResponse | None = Field(None, description="WireGuard status")
    outline: ServerStatusResponse | None = Field(None, description="Outline status")


class ServerStatsResponse(BaseModel):
    """Response schema for server statistics."""

    total_users: int = Field(..., description="Total users")
    active_users: int = Field(..., description="Active users")
    total_keys: int = Field(..., description="Total keys")
    active_keys: int = Field(..., description="Active keys")
    total_data_used_gb: float = Field(..., description="Total data used in GB")
    total_data_limit_gb: float = Field(..., description="Total data limit in GB")
    usage_percentage: float = Field(..., description="Usage percentage")
    servers: dict[str, Any] = Field(..., description="Server statuses")
    generated_at: str = Field(..., description="Generation timestamp")


# ============================================
# Admin Dashboard Schemas
# ============================================


class DashboardStatsResponse(BaseModel):
    """Response schema for dashboard statistics."""

    total_users: int = Field(..., description="Total users")
    active_users: int = Field(..., description="Active users")
    total_keys: int = Field(..., description="Total keys")
    active_keys: int = Field(..., description="Active keys")
    wireguard_keys: int = Field(..., description="WireGuard keys")
    wireguard_pct: float = Field(..., description="WireGuard percentage")
    outline_keys: int = Field(..., description="Outline keys")
    outline_pct: float = Field(..., description="Outline percentage")
    total_usage_gb: float = Field(..., description="Total usage in GB")
    avg_usage_gb: float = Field(..., description="Average usage per user")
    total_revenue: float = Field(..., description="Total revenue")
    new_users_today: int = Field(..., description="New users today")
    keys_created_today: int = Field(..., description="Keys created today")
    generated_at: str = Field(..., description="Generation timestamp")


# ============================================
# Admin Operation Result Schemas
# ============================================


class AdminOperationResultResponse(BaseModel):
    """Response schema for admin operation results."""

    success: bool = Field(..., description="Whether operation was successful")
    operation: str = Field(..., description="Operation name")
    target_id: str = Field(..., description="Target ID")
    message: str = Field(..., description="Result message")
    details: dict[str, Any] | None = Field(None, description="Additional details")
    timestamp: datetime = Field(..., description="Operation timestamp")

    model_config = {"from_attributes": True}


# ============================================
# Request Schemas
# ============================================


class UpdateUserStatusRequest(BaseModel):
    """Request schema for updating user status."""

    status: str = Field(..., description="New status (ACTIVE, SUSPENDED, BLOCKED)")


class AssignRoleRequest(BaseModel):
    """Request schema for assigning role to user."""

    role: str = Field(..., description="Role to assign (ADMIN, USER)")
    duration_days: int | None = Field(None, description="Role duration in days")


class ToggleKeyStatusRequest(BaseModel):
    """Request schema for toggling key status."""

    active: bool = Field(..., description="Whether key should be active")


class DeleteKeyResponse(BaseModel):
    """Response schema for key deletion."""

    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Result message")
    key_id: str = Field(..., description="Deleted key ID")
    server_deleted: bool | None = Field(None, description="Whether deleted from server")
    db_deleted: bool | None = Field(None, description="Whether deleted from database")
