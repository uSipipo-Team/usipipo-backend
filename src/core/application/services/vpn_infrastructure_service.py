"""VpnInfrastructureService - Central service for VPN infrastructure management."""

from typing import Any
from uuid import UUID

from usipipo_commons.domain.entities.vpn_key import VpnKey
from usipipo_commons.domain.enums.key_type import KeyType

from src.core.domain.interfaces.i_user_repository import IUserRepository
from src.core.domain.interfaces.i_vpn_key_repository import IVpnKeyRepository
from src.infrastructure.vpn_providers.outline_client import OutlineClient
from src.infrastructure.vpn_providers.wireguard_client import WireGuardClient


class VpnInfrastructureService:
    """
    Servicio central para gestión de infraestructura VPN.
    Coordina operaciones entre clientes VPN y repositorios.
    """

    def __init__(
        self,
        key_repository: IVpnKeyRepository,
        user_repository: IUserRepository,
        wireguard_client: WireGuardClient | None = None,
        outline_client: OutlineClient | None = None,
    ):
        """
        Inicializa el servicio de infraestructura VPN.

        Args:
            key_repository: Repositorio de claves VPN
            user_repository: Repositorio de usuarios
            wireguard_client: Cliente de WireGuard
            outline_client: Cliente de Outline
        """
        self.key_repository = key_repository
        self.user_repository = user_repository
        self.wireguard_client = wireguard_client
        self.outline_client = outline_client

    async def enable_key(self, key_id: UUID, vpn_type: KeyType) -> dict[str, Any]:
        """
        Habilita una clave en el servidor VPN y actualiza la base de datos.

        Args:
            key_id: ID interno de la clave (UUID)
            vpn_type: Tipo de VPN (KeyType.WIREGUARD o KeyType.OUTLINE)

        Returns:
            Dict con {"success": bool, "error": str|None}
        """
        try:
            key = await self.key_repository.get_by_id(key_id)

            if not key:
                return {"success": False, "error": f"Key not found: {key_id}"}

            server_success = False

            if vpn_type == KeyType.WIREGUARD and self.wireguard_client:
                # WireGuard usa external_id como client_name
                server_success = await self.wireguard_client.enable_peer(key.external_id or "")
            elif vpn_type == KeyType.OUTLINE and self.outline_client:
                server_success = await self.outline_client.enable_key(key.external_id or "")
            else:
                return {"success": False, "error": f"Unsupported VPN type: {vpn_type}"}

            if server_success:
                # Actualizar estado en BD
                updated_key = VpnKey(
                    id=key.id,
                    user_id=key.user_id,
                    name=key.name,
                    key_type=key.key_type,
                    key_data=key.key_data,
                    external_id=key.external_id,
                    is_active=key.is_active,
                    created_at=key.created_at,
                    expires_at=key.expires_at,
                    last_seen_at=key.last_seen_at,
                    used_bytes=key.used_bytes,
                    data_limit_bytes=key.data_limit_bytes,
                    billing_reset_at=key.billing_reset_at,
                )
                await self.key_repository.update(updated_key)
                return {"success": True, "error": None}
            else:
                return {"success": False, "error": "Failed to enable key on server"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def disable_key(self, key_id: UUID, vpn_type: KeyType) -> dict[str, Any]:
        """
        Deshabilita una clave en el servidor VPN y actualiza la base de datos.

        Args:
            key_id: ID interno de la clave (UUID)
            vpn_type: Tipo de VPN (KeyType.WIREGUARD o KeyType.OUTLINE)

        Returns:
            Dict con {"success": bool, "error": str|None}
        """
        try:
            key = await self.key_repository.get_by_id(key_id)

            if not key:
                return {"success": False, "error": f"Key not found: {key_id}"}

            server_success = False

            if vpn_type == KeyType.WIREGUARD and self.wireguard_client:
                # WireGuard usa external_id como client_name
                server_success = await self.wireguard_client.disable_peer(key.external_id or "")
            elif vpn_type == KeyType.OUTLINE and self.outline_client:
                server_success = await self.outline_client.disable_key(key.external_id or "")
            else:
                return {"success": False, "error": f"Unsupported VPN type: {vpn_type}"}

            if server_success:
                # Actualizar estado en BD
                updated_key = VpnKey(
                    id=key.id,
                    user_id=key.user_id,
                    name=key.name,
                    key_type=key.key_type,
                    key_data=key.key_data,
                    external_id=key.external_id,
                    is_active=key.is_active,
                    created_at=key.created_at,
                    expires_at=key.expires_at,
                    last_seen_at=key.last_seen_at,
                    used_bytes=key.used_bytes,
                    data_limit_bytes=key.data_limit_bytes,
                    billing_reset_at=key.billing_reset_at,
                )
                await self.key_repository.update(updated_key)
                return {"success": True, "error": None}
            else:
                return {"success": False, "error": "Failed to disable key on server"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_key_usage_from_server(self, key_id: UUID, vpn_type: KeyType) -> dict[str, int]:
        """
        Obtiene el uso real de datos desde el servidor VPN.

        Args:
            key_id: ID interno de la clave (UUID)
            vpn_type: Tipo de VPN

        Returns:
            Dict con bytes_used, bytes_rx, bytes_tx
        """
        try:
            key = await self.key_repository.get_by_id(key_id)

            if not key:
                return {"bytes_used": 0, "bytes_rx": 0, "bytes_tx": 0}

            if vpn_type == KeyType.WIREGUARD and self.wireguard_client:
                # WireGuard usa external_id como client_name
                metrics = await self.wireguard_client.get_peer_metrics(key.external_id or "")
                return {
                    "bytes_used": metrics.get("transfer_total", 0),
                    "bytes_rx": metrics.get("transfer_rx", 0),
                    "bytes_tx": metrics.get("transfer_tx", 0),
                }
            elif vpn_type == KeyType.OUTLINE and self.outline_client:
                usage = await self.outline_client.get_key_usage(key.external_id or "")
                return {
                    "bytes_used": usage.get("bytes_used", 0),
                    "bytes_rx": usage.get("bytes_rx", 0),
                    "bytes_tx": usage.get("bytes_tx", 0),
                }
            else:
                return {"bytes_used": 0, "bytes_rx": 0, "bytes_tx": 0}

        except Exception:
            return {"bytes_used": 0, "bytes_rx": 0, "bytes_tx": 0}

    async def sync_all_keys_usage(self) -> dict[str, Any]:
        """
        Sincroniza el uso de datos de todas las claves activas.

        Returns:
            Dict con {"synced": int, "failed": int, "errors": list}
        """
        try:
            # Obtener todas las claves activas
            all_keys = await self.key_repository.get_by_user_id(
                UUID("00000000-0000-0000-0000-000000000000")
            )

            synced = 0
            failed = 0
            errors = []

            for key in all_keys:
                try:
                    usage = await self.get_key_usage_from_server(key.id, key.key_type)
                    bytes_used = usage.get("bytes_used", 0)

                    # Actualizar en BD
                    updated_key = VpnKey(
                        id=key.id,
                        user_id=key.user_id,
                        name=key.name,
                        key_type=key.key_type,
                        key_data=key.key_data,
                        external_id=key.external_id,
                        is_active=key.is_active,
                        created_at=key.created_at,
                        expires_at=key.expires_at,
                        last_seen_at=key.last_seen_at,
                        used_bytes=bytes_used,
                        data_limit_bytes=key.data_limit_bytes,
                        billing_reset_at=key.billing_reset_at,
                    )
                    await self.key_repository.update(updated_key)
                    synced += 1

                except Exception as e:
                    failed += 1
                    errors.append(f"Key {key.id}: {str(e)}")

            return {"synced": synced, "failed": failed, "errors": errors}

        except Exception as e:
            return {"synced": 0, "failed": 0, "errors": [str(e)]}
