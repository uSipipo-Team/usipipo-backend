"""VPN Key repository implementation with SQLAlchemy."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.vpn_key import VpnKey

from src.core.domain.interfaces.i_vpn_key_repository import IVpnKeyRepository
from src.infrastructure.persistence.models.vpn_key_model import VpnKeyModel


class VpnKeyRepository(IVpnKeyRepository):
    """SQLAlchemy implementation of VPN key repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, key_id: UUID) -> VpnKey | None:
        """Gets VPN key by ID."""
        result = await self.session.execute(select(VpnKeyModel).where(VpnKeyModel.id == key_id))
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_user_id(self, user_id: UUID) -> list[VpnKey]:
        """Gets all VPN keys for a user."""
        result = await self.session.execute(
            select(VpnKeyModel)
            .where(VpnKeyModel.user_id == user_id)
            .order_by(VpnKeyModel.created_at.desc())
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def create(self, vpn_key: VpnKey) -> VpnKey:
        """Creates a new VPN key."""
        model = VpnKeyModel.from_entity(vpn_key)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_entity()

    async def update(self, vpn_key: VpnKey) -> VpnKey:
        """Updates an existing VPN key."""
        model = VpnKeyModel.from_entity(vpn_key)
        await self.session.merge(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_entity()

    async def delete(self, key_id: UUID) -> bool:
        """Deletes a VPN key."""
        result = await self.session.execute(select(VpnKeyModel).where(VpnKeyModel.id == key_id))
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False
