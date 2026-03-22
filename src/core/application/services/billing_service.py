"""Billing service for usage tracking."""

from uuid import UUID

from src.core.application.exceptions import UserNotFoundError, VpnKeyNotFoundError
from src.core.domain.interfaces.i_user_repository import IUserRepository
from src.core.domain.interfaces.i_vpn_key_repository import IVpnKeyRepository


class BillingService:
    """Application service for billing and usage tracking."""

    def __init__(
        self,
        user_repo: IUserRepository,
        vpn_key_repo: IVpnKeyRepository,
    ):
        self.user_repo = user_repo
        self.vpn_key_repo = vpn_key_repo

    async def get_usage(self, user_id: UUID) -> dict:
        """Gets data usage for a user."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        keys = await self.vpn_key_repo.get_by_user_id(user_id)

        # Convertir bytes a GB
        total_used_gb = sum(key.used_bytes / (1024**3) for key in keys)
        total_limit_gb = sum(key.data_limit_bytes / (1024**3) for key in keys)

        return {
            "balance_gb": user.balance_gb,
            "total_purchased_gb": user.total_purchased_gb,
            "keys_count": len(keys),
            "data_used_gb": round(total_used_gb, 2),
            "data_limit_gb": round(total_limit_gb, 2),
            "usage_percentage": round(
                (total_used_gb / total_limit_gb * 100) if total_limit_gb > 0 else 0, 2
            ),
        }

    async def get_key_usage(self, user_id: UUID, key_id: UUID) -> dict:
        """Gets data usage for a specific key."""
        key = await self.vpn_key_repo.get_by_id(key_id)

        if not key:
            raise VpnKeyNotFoundError(f"Key {key_id} not found")

        if key.user_id != user_id:
            raise PermissionError("User does not own this key")

        # Convertir bytes a GB
        used_gb = key.used_bytes / (1024**3)
        limit_gb = key.data_limit_bytes / (1024**3)

        return {
            "key_id": str(key.id),
            "name": key.name,
            "data_used_gb": round(used_gb, 2),
            "data_limit_gb": round(limit_gb, 2),
            "usage_percentage": round((used_gb / limit_gb * 100) if limit_gb > 0 else 0, 2),
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
        }
