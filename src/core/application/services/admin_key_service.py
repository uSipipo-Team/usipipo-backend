"""
Administrative key management service for uSipipo backend.

This service is dedicated to VPN key management from the admin panel.
"""

import logging
from typing import TYPE_CHECKING, Any

from usipipo_commons.domain.entities.admin_key_info import AdminKeyInfo
from usipipo_commons.domain.entities.vpn_key import VpnKey

from src.core.domain.interfaces.i_admin_service import IAdminKeyService

if TYPE_CHECKING:
    from src.infrastructure.persistence.repositories.user_repository import UserRepository
    from src.infrastructure.persistence.repositories.vpn_repository import VpnRepository

logger = logging.getLogger(__name__)


class AdminKeyService(IAdminKeyService):
    """Service dedicated to VPN key management from admin panel."""

    def __init__(
        self,
        vpn_repository: "VpnRepository",
        user_repository: "UserRepository",
        wireguard_client: Any = None,
        outline_client: Any = None,
    ):
        self.vpn_repository = vpn_repository
        self.user_repository = user_repository
        self.wireguard_client = wireguard_client
        self.outline_client = outline_client

    async def get_user_keys(self, user_id: int) -> list[VpnKey]:
        """Get all keys of a specific user."""
        try:
            user = await self.user_repository.get_by_telegram_id(user_id)
            if not user:
                return []

            return await self.vpn_repository.get_by_user_id(user.id)
        except Exception as e:
            logger.error(f"Error getting keys for user {user_id}: {e}", exc_info=True)
            return []

    async def get_all_keys(self, current_user_id: int) -> list[AdminKeyInfo]:
        """Get all keys from all users."""
        try:
            all_keys = await self.vpn_repository.get_all()

            key_list = []
            for key in all_keys:
                user = await self.user_repository.get_by_id(key.user_id)
                user_name = user.first_name or "Unknown" if user else "Unknown"

                usage_stats = await self.get_key_usage_stats(str(key.id))

                key_info = AdminKeyInfo(
                    key_id=str(key.id),
                    user_id=user.telegram_id if user else 0,
                    user_name=user_name,
                    key_type=key.key_type.value
                    if hasattr(key.key_type, "value")
                    else str(key.key_type),
                    key_name=key.name,
                    access_url=key.key_data,
                    created_at=key.created_at,
                    last_used=key.last_seen_at,
                    data_limit=key.data_limit_bytes,
                    data_used=usage_stats.get("data_used", 0),
                    is_active=key.is_active,
                    server_status=usage_stats.get("server_status", "unknown"),
                )
                key_list.append(key_info)

            return key_list

        except Exception as e:
            logger.error(f"Error getting all keys: {e}", exc_info=True)
            return []

    async def delete_key_from_servers(self, key_id: str, key_type: str) -> bool:
        """Delete a key from VPN servers (WireGuard and Outline)."""
        try:
            from uuid import UUID

            key = await self.vpn_repository.get_by_id(UUID(key_id))
            if not key:
                logger.error(f"Key {key_id} not found in database")
                return False

            success = True

            if key_type.lower() == "wireguard" and self.wireguard_client:
                wg_result = await self.wireguard_client.delete_client(key.name)
                if not wg_result:
                    logger.error(f"Error deleting key {key_id} from WireGuard")
                    success = False
                else:
                    logger.info(f"Key {key_id} deleted from WireGuard")

            elif key_type.lower() == "outline" and self.outline_client:
                outline_result = await self.outline_client.delete_key(key_id)
                if not outline_result:
                    logger.error(f"Error deleting key {key_id} from Outline")
                    success = False
                else:
                    logger.info(f"Key {key_id} deleted from Outline")

            return success

        except Exception as e:
            logger.error(f"Error deleting key {key_id} from servers: {e}", exc_info=True)
            return False

    async def delete_key_from_db(self, key_id: str) -> bool:
        """Delete a key from database."""
        try:
            from uuid import UUID

            result = await self.vpn_repository.delete(UUID(key_id))
            if result:
                logger.info(f"Key {key_id} deleted from database")
            else:
                logger.warning(f"Key {key_id} not found in database")
            return result
        except Exception as e:
            logger.error(f"Error deleting key {key_id} from database: {e}", exc_info=True)
            return False

    async def delete_user_key_complete(self, key_id: str) -> dict[str, Any]:
        """Delete a key completely (servers + DB)."""
        try:
            from uuid import UUID

            key = await self.vpn_repository.get_by_id(UUID(key_id))
            if not key:
                return {
                    "success": False,
                    "message": f"Key {key_id} not found",
                    "key_id": key_id,
                }

            key_type = key.key_type.value if hasattr(key.key_type, "value") else str(key.key_type)
            server_result = await self.delete_key_from_servers(key_id, key_type)
            db_result = await self.delete_key_from_db(key_id)

            return {
                "success": server_result and db_result,
                "message": f"Key {key_id} deleted successfully",
                "key_id": key_id,
                "server_deleted": server_result,
                "db_deleted": db_result,
            }

        except Exception as e:
            logger.error(f"Error deleting key completely: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error deleting key: {str(e)}",
                "key_id": key_id,
            }

    async def toggle_key_status(self, key_id: str, active: bool) -> dict[str, Any]:
        """Activate or deactivate a VPN key."""
        try:
            from uuid import UUID

            key = await self.vpn_repository.get_by_id(UUID(key_id))
            if not key:
                return {
                    "success": False,
                    "message": f"Key {key_id} not found",
                }

            key.is_active = active
            await self.vpn_repository.update(key)

            return {
                "success": True,
                "message": f"Key {key_id} {'activated' if active else 'deactivated'}",
                "key_id": key_id,
                "is_active": active,
            }

        except Exception as e:
            logger.error(f"Error toggling key status: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error toggling key status: {str(e)}",
            }

    async def get_key_usage_stats(self, key_id: str) -> dict[str, Any]:
        """Get usage statistics for a key."""
        try:
            from uuid import UUID

            key = await self.vpn_repository.get_by_id(UUID(key_id))
            if not key:
                return {
                    "data_used": 0,
                    "server_status": "not_found",
                }

            data_used = key.data_used_bytes
            key_type = key.key_type.value if hasattr(key.key_type, "value") else str(key.key_type)
            server_status = "active" if key.is_active else "inactive"

            return {
                "data_used": data_used,
                "server_status": server_status,
                "key_type": key_type,
            }

        except Exception as e:
            logger.error(f"Error getting key usage stats: {e}", exc_info=True)
            return {
                "data_used": 0,
                "server_status": "error",
                "error": str(e),
            }
