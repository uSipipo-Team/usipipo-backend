"""Tests unitarios para SubscriptionRepository."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from usipipo_commons.domain.entities.subscription_plan import (
    PlanType,
    SubscriptionPlan,
)

from src.infrastructure.persistence.models.subscription_plan_model import SubscriptionPlanModel
from src.infrastructure.persistence.repositories.subscription_repository import (
    SubscriptionRepository,
)


@pytest.fixture
async def subscription_repo(test_session):
    """Crea una instancia de SubscriptionRepository."""
    return SubscriptionRepository(test_session)


@pytest.fixture
async def sample_subscription(test_session):
    """Crea una suscripción de ejemplo en la base de datos."""
    now = datetime.now(UTC)
    plan = SubscriptionPlan(
        id=uuid.uuid4(),
        user_id=123456,
        plan_type=PlanType.ONE_MONTH,
        stars_paid=360,
        payment_id="payment_test_123",
        starts_at=now,
        expires_at=now + timedelta(days=30),
        is_active=True,
    )

    model = SubscriptionPlanModel.from_entity(plan)
    test_session.add(model)
    await test_session.commit()
    await test_session.refresh(model)

    return plan


class TestSubscriptionRepositorySave:
    """Tests para el método save del repositorio."""

    @pytest.mark.asyncio
    async def test_save_creates_new_subscription(self, subscription_repo, test_session):
        """Verifica que save crea una nueva suscripción."""
        now = datetime.now(UTC)
        plan = SubscriptionPlan(
            id=None,
            user_id=123456,
            plan_type=PlanType.ONE_MONTH,
            stars_paid=360,
            payment_id="payment_new_123",
            starts_at=now,
            expires_at=now + timedelta(days=30),
            is_active=True,
        )

        result = await subscription_repo.save(plan, current_user_id=999999)

        assert result is not None
        assert result.id is not None
        assert result.user_id == 123456
        assert result.plan_type == PlanType.ONE_MONTH
        assert result.stars_paid == 360
        assert result.payment_id == "payment_new_123"

        # Verify in database
        db_result = await test_session.execute(
            select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == result.id)
        )
        db_model = db_result.scalar_one_or_none()
        assert db_model is not None
        assert db_model.payment_id == "payment_new_123"

    @pytest.mark.asyncio
    async def test_save_updates_existing_subscription(
        self, subscription_repo, test_session, sample_subscription
    ):
        """Verifica que save actualiza una suscripción existente."""
        # Modify the subscription
        updated_plan = SubscriptionPlan(
            id=sample_subscription.id,
            user_id=sample_subscription.user_id,
            plan_type=PlanType.THREE_MONTHS,
            stars_paid=960,
            payment_id=sample_subscription.payment_id,
            starts_at=sample_subscription.starts_at,
            expires_at=sample_subscription.expires_at,
            is_active=sample_subscription.is_active,
        )

        result = await subscription_repo.save(updated_plan, current_user_id=999999)

        assert result is not None
        assert result.id == sample_subscription.id
        assert result.plan_type == PlanType.THREE_MONTHS
        assert result.stars_paid == 960

        # Verify in database
        db_result = await test_session.execute(
            select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == sample_subscription.id)
        )
        db_model = db_result.scalar_one_or_none()
        assert db_model is not None
        assert db_model.plan_type == PlanType.THREE_MONTHS
        assert db_model.stars_paid == 960


class TestSubscriptionRepositoryGetById:
    """Tests para el método get_by_id del repositorio."""

    @pytest.mark.asyncio
    async def test_get_by_id_returns_subscription(
        self, subscription_repo, test_session, sample_subscription
    ):
        """Verifica que get_by_id retorna la suscripción correcta."""
        result = await subscription_repo.get_by_id(sample_subscription.id, current_user_id=999999)

        assert result is not None
        assert result.id == sample_subscription.id
        assert result.user_id == sample_subscription.user_id
        assert result.plan_type == sample_subscription.plan_type
        assert result.payment_id == sample_subscription.payment_id

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_for_nonexistent(self, subscription_repo, test_session):
        """Verifica que get_by_id retorna None para ID inexistente."""
        fake_id = uuid.uuid4()
        result = await subscription_repo.get_by_id(fake_id, current_user_id=999999)

        assert result is None


class TestSubscriptionRepositoryGetByPaymentId:
    """Tests para el método get_by_payment_id del repositorio."""

    @pytest.mark.asyncio
    async def test_get_by_payment_id_returns_subscription(
        self, subscription_repo, test_session, sample_subscription
    ):
        """Verifica que get_by_payment_id retorna la suscripción correcta."""
        result = await subscription_repo.get_by_payment_id(
            sample_subscription.payment_id, current_user_id=999999
        )

        assert result is not None
        assert result.id == sample_subscription.id
        assert result.payment_id == sample_subscription.payment_id

    @pytest.mark.asyncio
    async def test_get_by_payment_id_returns_none_for_nonexistent(
        self, subscription_repo, test_session
    ):
        """Verifica que get_by_payment_id retorna None para payment_id inexistente."""
        result = await subscription_repo.get_by_payment_id(
            "payment_nonexistent", current_user_id=999999
        )

        assert result is None


class TestSubscriptionRepositoryGetActiveByUser:
    """Tests para el método get_active_by_user del repositorio."""

    @pytest.mark.asyncio
    async def test_get_active_by_user_returns_active_subscription(
        self, subscription_repo, test_session, sample_subscription
    ):
        """Verifica que get_active_by_user retorna suscripción activa."""
        result = await subscription_repo.get_active_by_user(
            sample_subscription.user_id, current_user_id=999999
        )

        assert result is not None
        assert result.id == sample_subscription.id
        assert result.user_id == sample_subscription.user_id
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_get_active_by_user_returns_none_for_inactive(
        self, subscription_repo, test_session, sample_subscription
    ):
        """Verifica que get_active_by_user retorna None para suscripción inactiva."""
        # Deactivate the subscription
        sample_subscription.is_active = False
        model = SubscriptionPlanModel.from_entity(sample_subscription)
        await test_session.merge(model)
        await test_session.commit()

        result = await subscription_repo.get_active_by_user(
            sample_subscription.user_id, current_user_id=999999
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_active_by_user_returns_none_for_expired(
        self, subscription_repo, test_session
    ):
        """Verifica que get_active_by_user retorna None para suscripción expirada."""
        now = datetime.now(UTC)
        expired_plan = SubscriptionPlan(
            id=uuid.uuid4(),
            user_id=789012,
            plan_type=PlanType.ONE_MONTH,
            stars_paid=360,
            payment_id="payment_expired_test",
            starts_at=now - timedelta(days=60),
            expires_at=now - timedelta(days=30),
            is_active=True,
        )

        model = SubscriptionPlanModel.from_entity(expired_plan)
        test_session.add(model)
        await test_session.commit()

        result = await subscription_repo.get_active_by_user(789012, current_user_id=999999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_active_by_user_returns_newest_for_multiple_active(
        self, subscription_repo, test_session
    ):
        """Verifica que get_active_by_user retorna la suscripción con expiración más lejana."""
        now = datetime.now(UTC)

        # Create two active subscriptions with different expiration dates
        plan1 = SubscriptionPlan(
            id=uuid.uuid4(),
            user_id=345678,
            plan_type=PlanType.ONE_MONTH,
            stars_paid=360,
            payment_id="payment_multi_1",
            starts_at=now,
            expires_at=now + timedelta(days=30),
            is_active=True,
        )

        plan2 = SubscriptionPlan(
            id=uuid.uuid4(),
            user_id=345678,
            plan_type=PlanType.THREE_MONTHS,
            stars_paid=960,
            payment_id="payment_multi_2",
            starts_at=now,
            expires_at=now + timedelta(days=90),
            is_active=True,
        )

        for plan in [plan1, plan2]:
            model = SubscriptionPlanModel.from_entity(plan)
            test_session.add(model)
        await test_session.commit()

        result = await subscription_repo.get_active_by_user(345678, current_user_id=999999)

        assert result is not None
        assert result.plan_type == PlanType.THREE_MONTHS
        assert result.expires_at == plan2.expires_at


class TestSubscriptionRepositoryGetExpiringPlans:
    """Tests para el método get_expiring_plans del repositorio."""

    @pytest.mark.asyncio
    async def test_get_expiring_plans_returns_expiring_soon(self, subscription_repo, test_session):
        """Verifica que get_expiring_plans retorna planes que expiran pronto."""
        now = datetime.now(UTC)

        # Create subscription expiring in 2 days
        expiring_plan = SubscriptionPlan(
            id=uuid.uuid4(),
            user_id=456789,
            plan_type=PlanType.ONE_MONTH,
            stars_paid=360,
            payment_id="payment_expiring_soon",
            starts_at=now - timedelta(days=28),
            expires_at=now + timedelta(days=2),
            is_active=True,
        )

        model = SubscriptionPlanModel.from_entity(expiring_plan)
        test_session.add(model)
        await test_session.commit()

        result = await subscription_repo.get_expiring_plans(days=3, current_user_id=999999)

        assert len(result) == 1
        assert result[0].id == expiring_plan.id
        assert result[0].payment_id == "payment_expiring_soon"

    @pytest.mark.asyncio
    async def test_get_expiring_plans_excludes_not_expiring_soon(
        self, subscription_repo, test_session
    ):
        """Verifica que get_expiring_plans excluye planes que no expiran pronto."""
        now = datetime.now(UTC)

        # Create subscription expiring in 10 days
        not_expiring_plan = SubscriptionPlan(
            id=uuid.uuid4(),
            user_id=567890,
            plan_type=PlanType.ONE_MONTH,
            stars_paid=360,
            payment_id="payment_not_expiring",
            starts_at=now,
            expires_at=now + timedelta(days=10),
            is_active=True,
        )

        model = SubscriptionPlanModel.from_entity(not_expiring_plan)
        test_session.add(model)
        await test_session.commit()

        result = await subscription_repo.get_expiring_plans(days=3, current_user_id=999999)

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_expiring_plans_excludes_inactive(self, subscription_repo, test_session):
        """Verifica que get_expiring_plans excluye planes inactivos."""
        now = datetime.now(UTC)

        # Create inactive subscription expiring soon
        inactive_plan = SubscriptionPlan(
            id=uuid.uuid4(),
            user_id=678901,
            plan_type=PlanType.ONE_MONTH,
            stars_paid=360,
            payment_id="payment_inactive",
            starts_at=now - timedelta(days=28),
            expires_at=now + timedelta(days=2),
            is_active=False,
        )

        model = SubscriptionPlanModel.from_entity(inactive_plan)
        test_session.add(model)
        await test_session.commit()

        result = await subscription_repo.get_expiring_plans(days=3, current_user_id=999999)

        assert len(result) == 0


class TestSubscriptionRepositoryGetExpiredPlans:
    """Tests para el método get_expired_plans del repositorio."""

    @pytest.mark.asyncio
    async def test_get_expired_plans_returns_expired(self, subscription_repo, test_session):
        """Verifica que get_expired_plans retorna planes expirados."""
        now = datetime.now(UTC)

        # Create expired subscription
        expired_plan = SubscriptionPlan(
            id=uuid.uuid4(),
            user_id=789012,
            plan_type=PlanType.ONE_MONTH,
            stars_paid=360,
            payment_id="payment_expired",
            starts_at=now - timedelta(days=60),
            expires_at=now - timedelta(days=30),
            is_active=True,
        )

        model = SubscriptionPlanModel.from_entity(expired_plan)
        test_session.add(model)
        await test_session.commit()

        result = await subscription_repo.get_expired_plans(current_user_id=999999)

        assert len(result) == 1
        assert result[0].id == expired_plan.id
        assert result[0].payment_id == "payment_expired"

    @pytest.mark.asyncio
    async def test_get_expired_plans_excludes_active(self, subscription_repo, test_session):
        """Verifica que get_expired_plans excluye planes activos."""
        now = datetime.now(UTC)

        # Create active subscription
        active_plan = SubscriptionPlan(
            id=uuid.uuid4(),
            user_id=890123,
            plan_type=PlanType.ONE_MONTH,
            stars_paid=360,
            payment_id="payment_active_future",
            starts_at=now,
            expires_at=now + timedelta(days=30),
            is_active=True,
        )

        model = SubscriptionPlanModel.from_entity(active_plan)
        test_session.add(model)
        await test_session.commit()

        result = await subscription_repo.get_expired_plans(current_user_id=999999)

        assert len(result) == 0


class TestSubscriptionRepositoryDeactivate:
    """Tests para el método deactivate del repositorio."""

    @pytest.mark.asyncio
    async def test_deactivate_returns_true_for_existing(
        self, subscription_repo, test_session, sample_subscription
    ):
        """Verifica que deactivate retorna True para suscripción existente."""
        result = await subscription_repo.deactivate(sample_subscription.id, current_user_id=999999)

        assert result is True

        # Verify in database
        db_result = await test_session.execute(
            select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == sample_subscription.id)
        )
        db_model = db_result.scalar_one_or_none()
        assert db_model is not None
        assert db_model.is_active is False

    @pytest.mark.asyncio
    async def test_deactivate_returns_false_for_nonexistent(self, subscription_repo, test_session):
        """Verifica que deactivate retorna False para ID inexistente."""
        fake_id = uuid.uuid4()
        result = await subscription_repo.deactivate(fake_id, current_user_id=999999)

        assert result is False


class TestSubscriptionRepositoryGetByUserPaginated:
    """Tests para el método get_by_user_paginated del repositorio."""

    @pytest.mark.asyncio
    async def test_get_by_user_paginated_returns_subscriptions(
        self, subscription_repo, test_session
    ):
        """Verifica que get_by_user_paginated retorna suscripciones paginadas."""
        now = datetime.now(UTC)
        user_id = 111222

        # Create multiple subscriptions for the same user
        for i in range(5):
            plan = SubscriptionPlan(
                id=uuid.uuid4(),
                user_id=user_id,
                plan_type=PlanType.ONE_MONTH,
                stars_paid=360,
                payment_id=f"payment_page_test_{i}",
                starts_at=now,
                expires_at=now + timedelta(days=30),
                is_active=True,
            )
            model = SubscriptionPlanModel.from_entity(plan)
            test_session.add(model)
        await test_session.commit()

        # Get first page
        result = await subscription_repo.get_by_user_paginated(
            user_id=user_id, limit=2, offset=0, current_user_id=999999
        )

        assert len(result) == 2

        # Get second page
        result = await subscription_repo.get_by_user_paginated(
            user_id=user_id, limit=2, offset=2, current_user_id=999999
        )

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_by_user_paginated_returns_empty_for_no_results(
        self, subscription_repo, test_session
    ):
        """Verifica que get_by_user_paginated retorna lista vacía sin resultados."""
        result = await subscription_repo.get_by_user_paginated(
            user_id=999888, limit=10, offset=0, current_user_id=999999
        )

        assert len(result) == 0


class TestSubscriptionRepositoryCountByUser:
    """Tests para el método count_by_user del repositorio."""

    @pytest.mark.asyncio
    async def test_count_by_user_returns_correct_count(self, subscription_repo, test_session):
        """Verifica que count_by_user retorna el conteo correcto."""
        now = datetime.now(UTC)
        user_id = 333444

        # Create 3 subscriptions for the user
        for i in range(3):
            plan = SubscriptionPlan(
                id=uuid.uuid4(),
                user_id=user_id,
                plan_type=PlanType.ONE_MONTH,
                stars_paid=360,
                payment_id=f"payment_count_test_{i}",
                starts_at=now,
                expires_at=now + timedelta(days=30),
                is_active=True,
            )
            model = SubscriptionPlanModel.from_entity(plan)
            test_session.add(model)
        await test_session.commit()

        count = await subscription_repo.count_by_user(user_id=user_id, current_user_id=999999)

        assert count == 3

    @pytest.mark.asyncio
    async def test_count_by_user_returns_zero_for_no_subscriptions(
        self, subscription_repo, test_session
    ):
        """Verifica que count_by_user retorna 0 sin suscripciones."""
        count = await subscription_repo.count_by_user(user_id=555666, current_user_id=999999)

        assert count == 0
