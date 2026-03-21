"""
Administrative statistics service for uSipipo backend.

This service is dedicated to generating statistics for the admin panel.
"""

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from src.core.domain.interfaces.i_admin_service import IAdminStatsService

if TYPE_CHECKING:
    from src.infrastructure.persistence.repositories.payment_repository import PaymentRepository
    from src.infrastructure.persistence.repositories.user_repository import UserRepository
    from src.infrastructure.persistence.repositories.vpn_repository import VpnRepository

logger = logging.getLogger(__name__)


class AdminStatsService(IAdminStatsService):
    """Service dedicated to admin panel statistics."""

    def __init__(
        self,
        user_repository: "UserRepository",
        vpn_repository: "VpnRepository",
        payment_repository: "PaymentRepository",
    ):
        self.user_repository = user_repository
        self.vpn_repository = vpn_repository
        self.payment_repository = payment_repository

    async def get_dashboard_stats(self, current_user_id: int) -> dict[str, Any]:
        """
        Generate complete statistics for the administrative dashboard.
        Centralizes business logic to respect hexagonal architecture.
        """
        try:
            users = await self.user_repository.get_all()
            all_keys = await self.vpn_repository.get_all()

            total_users = len(users)
            active_users = sum(1 for u in users if getattr(u, "is_active", True))

            total_keys = len(all_keys)
            active_keys = sum(1 for k in all_keys if k.is_active)

            # Count keys by type
            wireguard_keys = sum(
                1
                for k in all_keys
                if hasattr(k.key_type, "value")
                and k.key_type.value.lower() == "wireguard"
                or str(k.key_type).lower() == "wireguard"
            )
            outline_keys = sum(
                1
                for k in all_keys
                if hasattr(k.key_type, "value")
                and k.key_type.value.lower() == "outline"
                or str(k.key_type).lower() == "outline"
            )

            wireguard_pct = round((wireguard_keys / total_keys * 100) if total_keys > 0 else 0, 1)
            outline_pct = round((outline_keys / total_keys * 100) if total_keys > 0 else 0, 1)

            # Calculate usage statistics
            total_usage_gb = sum(k.data_used_bytes for k in all_keys) / (1024**3)
            avg_usage = round(total_usage_gb / total_users, 2) if total_users > 0 else 0

            # Revenue and growth metrics
            total_revenue = await self._calculate_total_revenue()
            new_users_today = await self._calculate_new_users_today()
            keys_created_today = await self._calculate_keys_created_today()

            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_keys": total_keys,
                "active_keys": active_keys,
                "wireguard_keys": wireguard_keys,
                "wireguard_pct": wireguard_pct,
                "outline_keys": outline_keys,
                "outline_pct": outline_pct,
                "total_usage_gb": total_usage_gb,
                "avg_usage_gb": avg_usage,
                "total_revenue": total_revenue,
                "new_users_today": new_users_today,
                "keys_created_today": keys_created_today,
                "generated_at": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error generating dashboard statistics: {e}", exc_info=True)
            raise

    async def _calculate_total_revenue(self) -> float:
        """Calculate total system revenue."""
        try:
            transactions = await self.payment_repository.get_all()
            total_amount = sum(t.amount for t in transactions if t.amount > 0)
            return round(total_amount / 100.0, 2)
        except Exception as e:
            logger.error(f"Error calculating total revenue: {e}")
            return 0.0

    async def _calculate_new_users_today(self) -> int:
        """Calculate number of users registered today."""
        try:
            users = await self.user_repository.get_all()
            today = datetime.now(UTC).date()
            return sum(1 for u in users if u.created_at.date() == today)
        except Exception as e:
            logger.error(f"Error calculating new users today: {e}")
            return 0

    async def _calculate_keys_created_today(self) -> int:
        """Calculate number of keys created today."""
        try:
            all_keys = await self.vpn_repository.get_all()
            today = datetime.now(UTC).date()
            return sum(1 for k in all_keys if k.created_at.date() == today)
        except Exception as e:
            logger.error(f"Error calculating keys created today: {e}")
            return 0
