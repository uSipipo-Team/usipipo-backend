"""VPN Providers - Clientes para infraestructura VPN."""

from src.infrastructure.vpn_providers.outline_client import OutlineClient
from src.infrastructure.vpn_providers.wireguard_client import WireGuardClient

__all__ = ["OutlineClient", "WireGuardClient"]
