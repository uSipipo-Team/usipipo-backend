"""Implementación del repositorio de referidos con SQLAlchemy."""

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.referral import Referral

from src.core.domain.interfaces.i_referral_repository import IReferralRepository
from src.infrastructure.persistence.models.referral_model import ReferralModel


class ReferralRepository(IReferralRepository):
    """Implementación de repositorio de referidos con SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, referral: Referral) -> Referral:
        """Guarda o actualiza una relación de referido."""
        model = ReferralModel.from_entity(referral)
        await self.session.merge(model)
        await self.session.commit()
        return model.to_entity()

    async def get_by_id(self, referral_id: uuid.UUID) -> Referral | None:
        """Obtiene un referido por su ID."""
        result = await self.session.execute(
            select(ReferralModel).where(ReferralModel.id == referral_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_referred_id(self, referred_id: uuid.UUID) -> Referral | None:
        """Busca quién refirió a un usuario específico."""
        result = await self.session.execute(
            select(ReferralModel).where(ReferralModel.referred_id == referred_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_referrals_by_referrer(self, referrer_id: uuid.UUID) -> list[Referral]:
        """Obtiene la lista de usuarios referidos por alguien."""
        result = await self.session.execute(
            select(ReferralModel).where(ReferralModel.referrer_id == referrer_id)
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def count_referrals_by_referrer(self, referrer_id: uuid.UUID) -> int:
        """Cuenta el total de referidos de un usuario."""
        result = await self.session.execute(
            select(func.count()).where(ReferralModel.referrer_id == referrer_id)
        )
        return result.scalar() or 0

    async def mark_bonus_applied(self, referral_id: uuid.UUID) -> bool:
        """Marca un bono de referido como ya aplicado."""
        try:
            query = (
                update(ReferralModel)
                .where(ReferralModel.id == referral_id)
                .values(bonus_applied=True)
            )
            await self.session.execute(query)
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            return False
