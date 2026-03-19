"""Repositorio de claves VPN con SQLAlchemy."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from usipipo_commons.domain.entities.vpn_key import VpnKey
from src.core.domain.interfaces.i_vpn_repository import IVPNRepository
from src.infrastructure.persistence.models.vpn_key_model import VpnKeyModel


class VpnRepository(IVPNRepository):
    """Implementación de repositorio de claves VPN con SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, key_id: UUID) -> Optional[VpnKey]:
        """
        Obtiene clave VPN por ID.

        Args:
            key_id: UUID de la clave

        Returns:
            VpnKey o None si no existe
        """
        result = await self.session.execute(
            select(VpnKeyModel).where(VpnKeyModel.id == key_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_user_id(self, user_id: UUID) -> List[VpnKey]:
        """
        Obtiene todas las claves VPN de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Lista de claves VPN
        """
        result = await self.session.execute(
            select(VpnKeyModel).where(VpnKeyModel.user_id == user_id)
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def create(self, vpn_key: VpnKey) -> VpnKey:
        """
        Crea una nueva clave VPN.

        Args:
            vpn_key: Clave VPN a crear

        Returns:
            Clave VPN creada
        """
        model = VpnKeyModel.from_entity(vpn_key)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_entity()

    async def update(self, vpn_key: VpnKey) -> VpnKey:
        """
        Actualiza clave VPN existente.

        Args:
            vpn_key: Clave VPN con datos actualizados

        Returns:
            Clave VPN actualizada
        """
        model = VpnKeyModel.from_entity(vpn_key)
        await self.session.merge(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_entity()

    async def delete(self, key_id: UUID) -> bool:
        """
        Elimina clave VPN.

        Args:
            key_id: UUID de la clave

        Returns:
            True si se eliminó, False si no existía
        """
        result = await self.session.execute(
            select(VpnKeyModel).where(VpnKeyModel.id == key_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False
