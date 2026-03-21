"""VPN Key repository implementation with SQLAlchemy."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.vpn_key import VpnKey
from usipipo_commons.domain.enums.key_status import KeyStatus

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

    async def update_usage(self, key_id: UUID, data_used_gb: float) -> bool:
        """Updates data usage for a VPN key."""
        result = await self.session.execute(select(VpnKeyModel).where(VpnKeyModel.id == key_id))
        model = result.scalar_one_or_none()
        if model:
            model.data_used_gb = data_used_gb
            model.last_used_at = datetime.now(UTC)
            await self.session.commit()
            return True
        return False

    async def reset_data_usage(self, key_id: UUID) -> bool:
        """Resets data usage for a VPN key (new billing cycle)."""
        result = await self.session.execute(select(VpnKeyModel).where(VpnKeyModel.id == key_id))
        model = result.scalar_one_or_none()
        if model:
            model.data_used_gb = 0.0
            model.billing_reset_at = datetime.now(UTC)
            await self.session.commit()
            return True
        return False

    async def update_data_limit(self, key_id: UUID, data_limit_gb: float) -> bool:
        """Updates data limit for a VPN key."""
        result = await self.session.execute(select(VpnKeyModel).where(VpnKeyModel.id == key_id))
        model = result.scalar_one_or_none()
        if model:
            model.data_limit_gb = data_limit_gb
            await self.session.commit()
            return True
        return False

    async def get_keys_needing_reset(self) -> list[VpnKey]:
        """Gets keys that need billing cycle reset."""
        now = datetime.now(UTC)
        result = await self.session.execute(
            select(VpnKeyModel).where(
                VpnKeyModel.billing_reset_at < now,
                VpnKeyModel.status == KeyStatus.ACTIVE.value,
            )
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def get_all_active(self) -> list[VpnKey]:
        """Gets all active VPN keys in the system."""
        result = await self.session.execute(
            select(VpnKeyModel).where(VpnKeyModel.status == KeyStatus.ACTIVE.value)
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def get_all_keys(self) -> list[VpnKey]:
        """Gets all VPN keys in the system (active and inactive)."""
        result = await self.session.execute(select(VpnKeyModel))
        models = result.scalars().all()
        return [model.to_entity() for model in models]
