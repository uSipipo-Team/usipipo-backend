"""SQLAlchemy repository for subscription plans."""

import uuid
from dataclasses import replace
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.subscription_plan import SubscriptionPlan

from src.core.domain.interfaces.i_subscription_repository import ISubscriptionRepository
from src.infrastructure.persistence.models.subscription_plan_model import SubscriptionPlanModel


class SubscriptionRepository(ISubscriptionRepository):
    """SQLAlchemy implementation of ISubscriptionRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, plan: SubscriptionPlan, current_user_id: int) -> SubscriptionPlan:
        """Save or update a subscription plan."""
        model = SubscriptionPlanModel.from_entity(plan)

        if plan.id:
            # Update existing plan
            existing_result = await self.session.execute(
                select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == plan.id)
            )
            existing = existing_result.scalar_one_or_none()
            if existing:
                merged = await self.session.merge(model)
                await self.session.commit()
                await self.session.refresh(merged)
                return replace(plan)

        # Create new plan
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return replace(plan, id=model.id)

    async def get_by_id(self, plan_id: uuid.UUID, current_user_id: int) -> SubscriptionPlan | None:
        """Get subscription by ID."""
        result = await self.session.execute(
            select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == plan_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_payment_id(
        self, payment_id: str, current_user_id: int
    ) -> SubscriptionPlan | None:
        """Get subscription by payment ID (for idempotency)."""
        result = await self.session.execute(
            select(SubscriptionPlanModel).where(SubscriptionPlanModel.payment_id == payment_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_active_by_user(
        self, user_id: int, current_user_id: int
    ) -> SubscriptionPlan | None:
        """Get active subscription for a user."""
        result = await self.session.execute(
            select(SubscriptionPlanModel)
            .where(
                SubscriptionPlanModel.user_id == user_id,
                SubscriptionPlanModel.is_active,
                SubscriptionPlanModel.expires_at > datetime.now(UTC),
            )
            .order_by(SubscriptionPlanModel.expires_at.desc())
        )
        model = result.scalars().first()
        return model.to_entity() if model else None

    async def get_expiring_plans(self, days: int, current_user_id: int) -> list[SubscriptionPlan]:
        """Get plans expiring within N days."""
        now = datetime.now(UTC)
        future_date = now + timedelta(days=days)

        result = await self.session.execute(
            select(SubscriptionPlanModel)
            .where(
                SubscriptionPlanModel.is_active,
                SubscriptionPlanModel.expires_at > now,
                SubscriptionPlanModel.expires_at <= future_date,
            )
            .order_by(SubscriptionPlanModel.expires_at.asc())
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def get_expired_plans(self, current_user_id: int) -> list[SubscriptionPlan]:
        """Get all expired plans."""
        now = datetime.now(UTC)

        result = await self.session.execute(
            select(SubscriptionPlanModel)
            .where(
                SubscriptionPlanModel.is_active,
                SubscriptionPlanModel.expires_at <= now,
            )
            .order_by(SubscriptionPlanModel.expires_at.desc())
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def deactivate(self, plan_id: uuid.UUID, current_user_id: int) -> bool:
        """Deactivate a subscription plan."""
        result = await self.session.execute(
            select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == plan_id)
        )
        model = result.scalar_one_or_none()

        if not model:
            return False

        model.is_active = False
        model.updated_at = datetime.now(UTC)
        await self.session.commit()
        return True

    async def get_by_user_paginated(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
        current_user_id: int = 0,
    ) -> list[SubscriptionPlan]:
        """Get subscriptions for a user with pagination."""
        result = await self.session.execute(
            select(SubscriptionPlanModel)
            .where(SubscriptionPlanModel.user_id == user_id)
            .order_by(SubscriptionPlanModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def count_by_user(self, user_id: int, current_user_id: int = 0) -> int:
        """Count total subscriptions for a user."""
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count(SubscriptionPlanModel.id)).where(
                SubscriptionPlanModel.user_id == user_id
            )
        )
        return result.scalar() or 0
