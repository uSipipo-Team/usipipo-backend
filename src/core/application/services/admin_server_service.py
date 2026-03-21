"""
Administrative server management service for uSipipo backend.

This service is dedicated to VPN server management from the admin panel.
"""

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from usipipo_commons.domain.entities.server_status import ServerStatus

from src.core.domain.interfaces.i_admin_service import IAdminServerService

if TYPE_CHECKING:
    from src.infrastructure.persistence.repositories.user_repository import UserRepository
    from src.infrastructure.persistence.repositories.vpn_repository import VpnRepository

logger = logging.getLogger(__name__)


class AdminServerService(IAdminServerService):
    """Service dedicated to VPN server management from admin panel."""

    def __init__(
        self,
        user_repository: "UserRepository",
        vpn_repository: "VpnRepository",
        wireguard_client: Any = None,
        outline_client: Any = None,
    ):
        self.user_repository = user_repository
        self.vpn_repository = vpn_repository
        self.wireguard_client = wireguard_client
        self.outline_client = outline_client

    async def get_server_status(self) -> dict[str, ServerStatus]:
        """Get VPN server status."""
        try:
            status = {}

            # WireGuard server status
            try:
                wg_keys = await self.vpn_repository.get_all()
                wg_active_keys = [
                    k
                    for k in wg_keys
                    if k.is_active
                    and (
                        hasattr(k.key_type, "value")
                        and k.key_type.value.lower() == "wireguard"
                        or str(k.key_type).lower() == "wireguard"
                    )
                ]

                wg_status = ServerStatus(
                    server_type="wireguard",
                    is_healthy=True,
                    total_keys=len(
                        [
                            k
                            for k in wg_keys
                            if hasattr(k.key_type, "value")
                            and k.key_type.value.lower() == "wireguard"
                            or str(k.key_type).lower() == "wireguard"
                        ]
                    ),
                    active_keys=len(wg_active_keys),
                    version="1.0.0",
                    uptime="Unknown",
                    error_message=None,
                )
                status["wireguard"] = wg_status
            except Exception as e:
                wg_status = ServerStatus(
                    server_type="wireguard",
                    is_healthy=False,
                    total_keys=0,
                    active_keys=0,
                    version=None,
                    uptime=None,
                    error_message=str(e),
                )
                status["wireguard"] = wg_status
                logger.error(f"Error getting WireGuard status: {e}")

            # Outline server status
            try:
                outline_keys = await self.vpn_repository.get_all()
                outline_active_keys = [
                    k
                    for k in outline_keys
                    if k.is_active
                    and (
                        hasattr(k.key_type, "value")
                        and k.key_type.value.lower() == "outline"
                        or str(k.key_type).lower() == "outline"
                    )
                ]

                outline_status = ServerStatus(
                    server_type="outline",
                    is_healthy=True,
                    total_keys=len(
                        [
                            k
                            for k in outline_keys
                            if hasattr(k.key_type, "value")
                            and k.key_type.value.lower() == "outline"
                            or str(k.key_type).lower() == "outline"
                        ]
                    ),
                    active_keys=len(outline_active_keys),
                    version="1.0.0",
                    uptime="Unknown",
                    error_message=None,
                )
                status["outline"] = outline_status
            except Exception as e:
                outline_status = ServerStatus(
                    server_type="outline",
                    is_healthy=False,
                    total_keys=0,
                    active_keys=0,
                    version=None,
                    uptime=None,
                    error_message=str(e),
                )
                status["outline"] = outline_status
                logger.error(f"Error getting Outline status: {e}")

            return status

        except Exception as e:
            logger.error(f"Error getting server status: {e}", exc_info=True)
            return {}

    async def get_server_stats(self, current_user_id: int) -> dict[str, Any]:
        """Get server statistics for admin panel."""
        try:
            users = await self.user_repository.get_all()
            all_keys = await self.vpn_repository.get_all()
            server_status = await self.get_server_status()

            total_users = len(users)
            active_users = sum(1 for u in users if getattr(u, "is_active", True))

            total_keys = len(all_keys)
            active_keys = sum(1 for k in all_keys if k.is_active)

            total_data_used = sum(k.data_used_bytes for k in all_keys)
            total_data_limit = sum(k.data_limit_bytes for k in all_keys)
            usage_pct = round(
                (total_data_used / total_data_limit * 100) if total_data_limit > 0 else 0, 2
            )

            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_keys": total_keys,
                "active_keys": active_keys,
                "total_data_used_gb": round(total_data_used / (1024**3), 2),
                "total_data_limit_gb": round(total_data_limit / (1024**3), 2),
                "usage_percentage": usage_pct,
                "servers": {k: v.__dict__ for k, v in server_status.items()},
                "generated_at": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting server stats: {e}", exc_info=True)
            return {
                "error": str(e),
                "generated_at": datetime.now(UTC).isoformat(),
            }
