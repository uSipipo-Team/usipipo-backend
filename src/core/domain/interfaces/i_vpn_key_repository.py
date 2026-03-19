"""Interface for VPN key repository."""

from abc import ABC, abstractmethod
from uuid import UUID

from usipipo_commons.domain.entities.vpn_key import VpnKey


class IVpnKeyRepository(ABC):
    """Contract for VPN key repository."""

    @abstractmethod
    async def get_by_id(self, key_id: UUID) -> VpnKey | None:
        """Gets VPN key by ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[VpnKey]:
        """Gets all VPN keys for a user."""
        pass

    @abstractmethod
    async def create(self, vpn_key: VpnKey) -> VpnKey:
        """Creates a new VPN key."""
        pass

    @abstractmethod
    async def update(self, vpn_key: VpnKey) -> VpnKey:
        """Updates an existing VPN key."""
        pass

    @abstractmethod
    async def delete(self, key_id: UUID) -> bool:
        """Deletes a VPN key."""
        pass
