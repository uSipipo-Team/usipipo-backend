"""Interfaces de repositorio para la capa de dominio."""

from abc import ABC, abstractmethod
from uuid import UUID

from usipipo_commons.domain.entities.vpn_key import VpnKey


class IVPNRepository(ABC):
    """Contrato para repositorio de claves VPN."""

    @abstractmethod
    async def get_all(self) -> list[VpnKey]:
        """Obtiene todas las claves VPN."""
        pass

    @abstractmethod
    async def get_by_id(self, key_id: UUID) -> VpnKey | None:
        """Obtiene clave VPN por ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[VpnKey]:
        """Obtiene todas las claves VPN de un usuario."""
        pass

    @abstractmethod
    async def create(self, vpn_key: VpnKey) -> VpnKey:
        """Crea una nueva clave VPN."""
        pass

    @abstractmethod
    async def update(self, vpn_key: VpnKey) -> VpnKey:
        """Actualiza clave VPN existente."""
        pass

    @abstractmethod
    async def delete(self, key_id: UUID) -> bool:
        """Elimina clave VPN."""
        pass
