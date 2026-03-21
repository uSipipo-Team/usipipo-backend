"""Interfaces para servicios de administración."""

from abc import ABC, abstractmethod
from typing import Any

from usipipo_commons.domain.entities.admin_key_info import AdminKeyInfo
from usipipo_commons.domain.entities.admin_operation_result import AdminOperationResult
from usipipo_commons.domain.entities.admin_user_info import AdminUserInfo
from usipipo_commons.domain.entities.server_status import ServerStatus
from usipipo_commons.domain.entities.vpn_key import VpnKey


class IAdminStatsService(ABC):
    """Interface for administrative statistics service."""

    @abstractmethod
    async def get_dashboard_stats(self, current_user_id: int) -> dict[str, Any]:
        """Generate complete statistics for admin dashboard."""
        pass


class IAdminUserService(ABC):
    """Interface for administrative user management service."""

    @abstractmethod
    async def get_all_users(self, current_user_id: int) -> list[AdminUserInfo]:
        """Get list of all registered users."""
        pass

    @abstractmethod
    async def get_users_paginated(
        self, page: int, per_page: int, current_user_id: int
    ) -> dict[str, Any]:
        """Get paginated users."""
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> AdminUserInfo | None:
        """Get detailed information of a user."""
        pass

    @abstractmethod
    async def update_user_status(self, user_id: int, status: str) -> AdminOperationResult:
        """Update user status (ACTIVE, SUSPENDED, BLOCKED)."""
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> AdminOperationResult:
        """Delete a user and associated keys."""
        pass

    @abstractmethod
    async def assign_role_to_user(
        self, user_id: int, role: str, duration_days: int | None = None
    ) -> AdminOperationResult:
        """Assign role to a user."""
        pass

    @abstractmethod
    async def block_user(self, user_id: int) -> AdminOperationResult:
        """Block a user."""
        pass

    @abstractmethod
    async def unblock_user(self, user_id: int) -> AdminOperationResult:
        """Unblock a user."""
        pass


class IAdminKeyService(ABC):
    """Interface for administrative key management service."""

    @abstractmethod
    async def get_user_keys(self, user_id: int) -> list[VpnKey]:
        """Get all keys of a specific user."""
        pass

    @abstractmethod
    async def get_all_keys(self, current_user_id: int) -> list[AdminKeyInfo]:
        """Get all keys from all users."""
        pass

    @abstractmethod
    async def delete_key_from_servers(self, key_id: str, key_type: str) -> bool:
        """Delete a key from VPN servers (WireGuard and Outline)."""
        pass

    @abstractmethod
    async def delete_key_from_db(self, key_id: str) -> bool:
        """Delete a key from database."""
        pass

    @abstractmethod
    async def delete_user_key_complete(self, key_id: str) -> dict[str, Any]:
        """Delete a key completely (servers + DB)."""
        pass

    @abstractmethod
    async def toggle_key_status(self, key_id: str, active: bool) -> dict[str, Any]:
        """Activate or deactivate a VPN key."""
        pass

    @abstractmethod
    async def get_key_usage_stats(self, key_id: str) -> dict[str, Any]:
        """Get usage statistics for a key."""
        pass


class IAdminServerService(ABC):
    """Interface for administrative server management service."""

    @abstractmethod
    async def get_server_status(self) -> dict[str, ServerStatus]:
        """Get VPN server status."""
        pass

    @abstractmethod
    async def get_server_stats(self, current_user_id: int) -> dict[str, Any]:
        """Get server statistics for admin panel."""
        pass
