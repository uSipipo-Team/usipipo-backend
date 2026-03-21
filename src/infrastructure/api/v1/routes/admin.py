"""
Admin API routes for uSipipo backend.

These routes provide administrative endpoints for managing users, VPN keys,
and server monitoring. All endpoints require admin privileges.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.user import User

from src.core.application.services.admin_key_service import AdminKeyService
from src.core.application.services.admin_server_service import AdminServerService
from src.core.application.services.admin_stats_service import AdminStatsService
from src.core.application.services.admin_user_service import AdminUserService
from src.infrastructure.api.v1.deps import get_db, require_admin
from src.infrastructure.persistence.repositories.payment_repository import PaymentRepository
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.repositories.vpn_repository import VpnRepository
from src.infrastructure.vpn_providers.outline_client import OutlineClient
from src.infrastructure.vpn_providers.wireguard_client import WireGuardClient
from src.shared.schemas.admin import (
    AdminKeyInfoResponse,
    AdminKeyListResponse,
    AdminOperationResultResponse,
    AdminUserListResponse,
    AssignRoleRequest,
    DashboardStatsResponse,
    DeleteKeyResponse,
    ServerStatsResponse,
    ServerStatusListResponse,
    ToggleKeyStatusRequest,
    UpdateUserStatusRequest,
)
from src.shared.schemas.admin import AdminUserListResponse as AdminUserListResponseSchema

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================
# Dependencies
# ============================================


async def get_admin_user_service(
    db: AsyncSession = Depends(get_db),
) -> AdminUserService:
    """Dependency to get AdminUserService."""
    user_repo = UserRepository(db)
    vpn_repo = VpnRepository(db)
    payment_repo = PaymentRepository(db)
    return AdminUserService(user_repo, vpn_repo, payment_repo)


async def get_admin_key_service(
    db: AsyncSession = Depends(get_db),
) -> AdminKeyService:
    """Dependency to get AdminKeyService."""
    user_repo = UserRepository(db)
    vpn_repo = VpnRepository(db)
    wireguard_client = WireGuardClient()
    outline_client = OutlineClient()
    return AdminKeyService(vpn_repo, user_repo, wireguard_client, outline_client)


async def get_admin_stats_service(
    db: AsyncSession = Depends(get_db),
) -> AdminStatsService:
    """Dependency to get AdminStatsService."""
    user_repo = UserRepository(db)
    vpn_repo = VpnRepository(db)
    payment_repo = PaymentRepository(db)
    return AdminStatsService(user_repo, vpn_repo, payment_repo)


async def get_admin_server_service(
    db: AsyncSession = Depends(get_db),
) -> AdminServerService:
    """Dependency to get AdminServerService."""
    user_repo = UserRepository(db)
    vpn_repo = VpnRepository(db)
    wireguard_client = WireGuardClient()
    outline_client = OutlineClient()
    return AdminServerService(user_repo, vpn_repo, wireguard_client, outline_client)


# ============================================
# Dashboard Statistics
# ============================================


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    admin: User = Depends(require_admin),
    stats_service: AdminStatsService = Depends(get_admin_stats_service),
) -> DashboardStatsResponse:
    """
    Get dashboard statistics for admin panel.

    Returns comprehensive statistics including:
    - User metrics (total, active, new today)
    - VPN key metrics (total, active, by type)
    - Usage statistics
    - Revenue metrics

    **Requires admin privileges**
    """
    stats = await stats_service.get_dashboard_stats(admin.telegram_id)
    return DashboardStatsResponse(**stats)


# ============================================
# User Management
# ============================================


@router.get("/users", response_model=AdminUserListResponseSchema)
async def get_all_users(
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminUserListResponseSchema:
    """
    Get all users with admin information.

    Returns a list of all users with detailed information including:
    - User details (name, username, telegram_id)
    - VPN key counts (total, active)
    - Balance and referral credits
    - Registration and activity dates

    **Requires admin privileges**
    """
    users = await user_service.get_all_users(admin.telegram_id)
    return AdminUserListResponseSchema(
        users=users,
        total=len(users),
        page=1,
        per_page=len(users),
        total_pages=1,
    )


@router.get("/users/paginated", response_model=AdminUserListResponse)
async def get_users_paginated(
    page: int = 1,
    per_page: int = 20,
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminUserListResponse:
    """
    Get paginated list of users.

    **Requires admin privileges**
    """
    result = await user_service.get_users_paginated(page, per_page, admin.telegram_id)
    return AdminUserListResponse(**result)


@router.post("/users/{user_id}/status", response_model=AdminOperationResultResponse)
async def update_user_status(
    user_id: int,
    request: UpdateUserStatusRequest,
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminOperationResultResponse:
    """
    Update user status (ACTIVE, SUSPENDED, BLOCKED).

    **Requires admin privileges**
    """
    result = await user_service.update_user_status(user_id, request.status)
    return AdminOperationResultResponse(
        success=result.success,
        operation=result.operation,
        target_id=result.target_id,
        message=result.message,
        details=result.details,
        timestamp=result.timestamp,
    )


@router.post("/users/{user_id}/role", response_model=AdminOperationResultResponse)
async def assign_role_to_user(
    user_id: int,
    request: AssignRoleRequest,
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminOperationResultResponse:
    """
    Assign role to a user (ADMIN, USER).

    **Requires admin privileges**
    """
    result = await user_service.assign_role_to_user(user_id, request.role, request.duration_days)
    return AdminOperationResultResponse(
        success=result.success,
        operation=result.operation,
        target_id=result.target_id,
        message=result.message,
        details=result.details,
        timestamp=result.timestamp,
    )


@router.post("/users/{user_id}/block", response_model=AdminOperationResultResponse)
async def block_user(
    user_id: int,
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminOperationResultResponse:
    """
    Block a user.

    **Requires admin privileges**
    """
    result = await user_service.block_user(user_id)
    return AdminOperationResultResponse(
        success=result.success,
        operation=result.operation,
        target_id=result.target_id,
        message=result.message,
        details=result.details,
        timestamp=result.timestamp,
    )


@router.post("/users/{user_id}/unblock", response_model=AdminOperationResultResponse)
async def unblock_user(
    user_id: int,
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminOperationResultResponse:
    """
    Unblock a user.

    **Requires admin privileges**
    """
    result = await user_service.unblock_user(user_id)
    return AdminOperationResultResponse(
        success=result.success,
        operation=result.operation,
        target_id=result.target_id,
        message=result.message,
        details=result.details,
        timestamp=result.timestamp,
    )


@router.delete("/users/{user_id}", response_model=AdminOperationResultResponse)
async def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminOperationResultResponse:
    """
    Delete a user and all associated VPN keys.

    **Requires admin privileges**
    """
    result = await user_service.delete_user(user_id)
    return AdminOperationResultResponse(
        success=result.success,
        operation=result.operation,
        target_id=result.target_id,
        message=result.message,
        details=result.details,
        timestamp=result.timestamp,
    )


# ============================================
# VPN Key Management
# ============================================


@router.get("/keys", response_model=AdminKeyListResponse)
async def get_all_keys(
    admin: User = Depends(require_admin),
    key_service: AdminKeyService = Depends(get_admin_key_service),
) -> AdminKeyListResponse:
    """
    Get all VPN keys from all users.

    Returns detailed information about each key including:
    - Key details (ID, name, type, access URL)
    - User information
    - Usage statistics
    - Server status

    **Requires admin privileges**
    """
    keys = await key_service.get_all_keys(admin.telegram_id)
    return AdminKeyListResponse(
        keys=keys,
        total=len(keys),
    )


@router.get("/users/{user_id}/keys", response_model=AdminKeyListResponse)
async def get_user_keys(
    user_id: int,
    admin: User = Depends(require_admin),
    key_service: AdminKeyService = Depends(get_admin_key_service),
) -> AdminKeyListResponse:
    """
    Get all VPN keys for a specific user.

    **Requires admin privileges**
    """
    keys = await key_service.get_user_keys(user_id)
    key_responses = [
        AdminKeyInfoResponse(
            key_id=str(k.id),
            user_id=k.user_id,
            user_name="",
            key_type=k.key_type.value if hasattr(k.key_type, "value") else str(k.key_type),
            key_name=k.name,
            access_url=k.key_data,
            created_at=k.created_at,
            last_used=k.last_seen_at,
            data_limit=k.data_limit_bytes,
            data_used=k.data_used_bytes,
            is_active=k.is_active,
            server_status="unknown",
        )
        for k in keys
    ]
    return AdminKeyListResponse(
        keys=key_responses,
        total=len(keys),
    )


@router.post("/keys/{key_id}/toggle", response_model=AdminOperationResultResponse)
async def toggle_key_status(
    key_id: str,
    request: ToggleKeyStatusRequest,
    admin: User = Depends(require_admin),
    key_service: AdminKeyService = Depends(get_admin_key_service),
) -> AdminOperationResultResponse:
    """
    Activate or deactivate a VPN key.

    **Requires admin privileges**
    """
    result = await key_service.toggle_key_status(key_id, request.active)
    return AdminOperationResultResponse(
        success=result["success"],
        operation="toggle_key_status",
        target_id=key_id,
        message=result["message"],
        details={"is_active": result.get("is_active")},
        timestamp=datetime.now(UTC),
    )


@router.delete("/keys/{key_id}", response_model=DeleteKeyResponse)
async def delete_key(
    key_id: str,
    admin: User = Depends(require_admin),
    key_service: AdminKeyService = Depends(get_admin_key_service),
) -> DeleteKeyResponse:
    """
    Delete a VPN key completely (from servers and database).

    **Requires admin privileges**
    """
    result = await key_service.delete_user_key_complete(key_id)
    return DeleteKeyResponse(
        success=result["success"],
        message=result["message"],
        key_id=key_id,
        server_deleted=result.get("server_deleted"),
        db_deleted=result.get("db_deleted"),
    )


# ============================================
# Server Management
# ============================================


@router.get("/servers/status", response_model=ServerStatusListResponse)
async def get_server_status(
    admin: User = Depends(require_admin),
    server_service: AdminServerService = Depends(get_admin_server_service),
) -> ServerStatusListResponse:
    """
    Get status of all VPN servers.

    Returns health status for:
    - WireGuard server
    - Outline server

    **Requires admin privileges**
    """
    status = await server_service.get_server_status()
    return ServerStatusListResponse(
        wireguard=status.get("wireguard"),
        outline=status.get("outline"),
    )


@router.get("/servers/stats", response_model=ServerStatsResponse)
async def get_server_stats(
    admin: User = Depends(require_admin),
    server_service: AdminServerService = Depends(get_admin_server_service),
) -> ServerStatsResponse:
    """
    Get comprehensive server statistics.

    Returns:
    - User statistics
    - Key statistics
    - Data usage
    - Server health status

    **Requires admin privileges**
    """
    stats = await server_service.get_server_stats(admin.telegram_id)
    return ServerStatsResponse(**stats)
