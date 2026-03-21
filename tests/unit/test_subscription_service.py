"""Tests unitarios para SubscriptionService."""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from usipipo_commons.domain.entities.subscription_plan import (
    PlanType,
    SubscriptionPlan,
)

from src.core.application.services.subscription_service import (
    SUBSCRIPTION_OPTIONS,
    SubscriptionOption,
    SubscriptionService,
)


@pytest.fixture
def mock_subscription_repo():
    """Crea un mock del repositorio de suscripciones."""
    repo = AsyncMock()
    repo.get_active_by_user = AsyncMock()
    repo.get_by_payment_id = AsyncMock()
    repo.save = AsyncMock()
    repo.deactivate = AsyncMock()
    repo.get_expiring_plans = AsyncMock()
    repo.get_expired_plans = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_user_paginated = AsyncMock()
    repo.count_by_user = AsyncMock()
    return repo


@pytest.fixture
def mock_user_repo():
    """Crea un mock del repositorio de usuarios."""
    repo = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_telegram_id = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def subscription_service(mock_subscription_repo, mock_user_repo):
    """Crea una instancia de SubscriptionService con repositorios mock."""
    return SubscriptionService(
        subscription_repo=mock_subscription_repo,
        user_repo=mock_user_repo,
    )


@pytest.fixture
def sample_subscription_plan():
    """Crea un plan de suscripción de ejemplo."""
    now = datetime.now(UTC)
    return SubscriptionPlan(
        id=uuid.uuid4(),
        user_id=123456,
        plan_type=PlanType.ONE_MONTH,
        stars_paid=360,
        payment_id="payment_123",
        starts_at=now,
        expires_at=now + timedelta(days=30),
        is_active=True,
    )


class TestGetAvailablePlans:
    """Tests para el método get_available_plans."""

    def test_returns_all_plans(self, subscription_service):
        """Verifica que retorna todos los planes disponibles."""
        plans = subscription_service.get_available_plans()

        assert len(plans) == 3
        assert all(isinstance(plan, SubscriptionOption) for plan in plans)
        assert plans[0].name == "1 Month"
        assert plans[1].name == "3 Months"
        assert plans[2].name == "6 Months"

    def test_returns_copy_not_reference(self, subscription_service):
        """Verifica que retorna una copia, no la referencia original."""
        plans = subscription_service.get_available_plans()
        plans.append(
            SubscriptionOption(
                name="Test",
                plan_type=PlanType.ONE_MONTH,
                duration_months=1,
                stars=100,
                usdt=1.0,
            )
        )

        # La lista original no debería modificarse
        assert len(subscription_service.get_available_plans()) == 3


class TestGetPlanOption:
    """Tests para el método get_plan_option."""

    def test_returns_plan_by_type(self, subscription_service):
        """Verifica que retorna el plan correcto por tipo."""
        plan = subscription_service.get_plan_option("one_month")

        assert plan is not None
        assert plan.plan_type == PlanType.ONE_MONTH
        assert plan.stars == 360
        assert plan.usdt == 2.99

    def test_returns_plan_three_months(self, subscription_service):
        """Verifica que retorna el plan de 3 meses."""
        plan = subscription_service.get_plan_option("three_months")

        assert plan is not None
        assert plan.plan_type == PlanType.THREE_MONTHS
        assert plan.stars == 960
        assert plan.usdt == 7.99
        assert plan.bonus_percent == 11

    def test_returns_plan_six_months(self, subscription_service):
        """Verifica que retorna el plan de 6 meses."""
        plan = subscription_service.get_plan_option("six_months")

        assert plan is not None
        assert plan.plan_type == PlanType.SIX_MONTHS
        assert plan.stars == 1560
        assert plan.usdt == 12.99
        assert plan.bonus_percent == 13

    def test_case_insensitive(self, subscription_service):
        """Verifica que el tipo de plan es case-insensitive."""
        plan1 = subscription_service.get_plan_option("ONE_MONTH")
        plan2 = subscription_service.get_plan_option("One_Month")
        plan3 = subscription_service.get_plan_option("one_month")

        assert plan1 is not None
        assert plan2 is not None
        assert plan3 is not None
        assert plan1.plan_type == plan2.plan_type == plan3.plan_type

    def test_returns_none_for_invalid_type(self, subscription_service):
        """Verifica que retorna None para tipo de plan inválido."""
        plan = subscription_service.get_plan_option("invalid_plan")
        assert plan is None

    def test_returns_none_for_empty_string(self, subscription_service):
        """Verifica que retorna None para string vacío."""
        plan = subscription_service.get_plan_option("")
        assert plan is None


class TestIsPremiumUser:
    """Tests para el método is_premium_user."""

    @pytest.mark.asyncio
    async def test_returns_true_for_active_subscription(
        self, subscription_service, mock_subscription_repo, sample_subscription_plan
    ):
        """Verifica que retorna True para suscripción activa."""
        mock_subscription_repo.get_active_by_user.return_value = sample_subscription_plan

        result = await subscription_service.is_premium_user(123456, 999999)

        assert result is True
        mock_subscription_repo.get_active_by_user.assert_called_once_with(123456, 999999)

    @pytest.mark.asyncio
    async def test_returns_false_for_no_subscription(
        self, subscription_service, mock_subscription_repo
    ):
        """Verifica que retorna False cuando no hay suscripción."""
        mock_subscription_repo.get_active_by_user.return_value = None

        result = await subscription_service.is_premium_user(123456, 999999)

        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_for_expired_subscription(
        self, subscription_service, mock_subscription_repo
    ):
        """Verifica que retorna False para suscripción expirada."""
        expired_plan = SubscriptionPlan(
            id=uuid.uuid4(),
            user_id=123456,
            plan_type=PlanType.ONE_MONTH,
            stars_paid=360,
            payment_id="payment_expired",
            starts_at=datetime.now(UTC) - timedelta(days=60),
            expires_at=datetime.now(UTC) - timedelta(days=30),
            is_active=True,
        )
        mock_subscription_repo.get_active_by_user.return_value = expired_plan

        result = await subscription_service.is_premium_user(123456, 999999)

        assert result is False


class TestGetUserSubscription:
    """Tests para el método get_user_subscription."""

    @pytest.mark.asyncio
    async def test_returns_active_subscription(
        self, subscription_service, mock_subscription_repo, sample_subscription_plan
    ):
        """Verifica que retorna la suscripción activa."""
        mock_subscription_repo.get_active_by_user.return_value = sample_subscription_plan

        result = await subscription_service.get_user_subscription(123456, 999999)

        assert result is not None
        assert result == sample_subscription_plan
        mock_subscription_repo.get_active_by_user.assert_called_once_with(123456, 999999)

    @pytest.mark.asyncio
    async def test_returns_none_when_no_subscription(
        self, subscription_service, mock_subscription_repo
    ):
        """Verifica que retorna None cuando no hay suscripción."""
        mock_subscription_repo.get_active_by_user.return_value = None

        result = await subscription_service.get_user_subscription(123456, 999999)

        assert result is None


class TestActivateSubscription:
    """Tests para el método activate_subscription."""

    @pytest.mark.asyncio
    async def test_activates_new_subscription(
        self,
        subscription_service,
        mock_subscription_repo,
        mock_user_repo,
        sample_subscription_plan,
    ):
        """Verifica que activa una nueva suscripción correctamente."""
        mock_subscription_repo.get_active_by_user.return_value = None
        mock_subscription_repo.get_by_payment_id.return_value = None
        mock_subscription_repo.save.return_value = sample_subscription_plan

        result = await subscription_service.activate_subscription(
            user_id=123456,
            plan_type="one_month",
            stars_paid=360,
            payment_id="payment_new",
            current_user_id=999999,
        )

        assert result is not None
        assert result.user_id == 123456
        assert result.plan_type == PlanType.ONE_MONTH
        assert result.stars_paid == 360
        mock_subscription_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_error_for_existing_active_subscription(
        self, subscription_service, mock_subscription_repo, sample_subscription_plan
    ):
        """Verifica que lanza error si ya existe suscripción activa."""
        mock_subscription_repo.get_active_by_user.return_value = sample_subscription_plan

        with pytest.raises(ValueError, match="already has an active subscription"):
            await subscription_service.activate_subscription(
                user_id=123456,
                plan_type="one_month",
                stars_paid=360,
                payment_id="payment_new",
                current_user_id=999999,
            )

    @pytest.mark.asyncio
    async def test_returns_existing_for_same_payment_id(
        self, subscription_service, mock_subscription_repo, sample_subscription_plan
    ):
        """Verifica idempotencia: retorna existente para mismo payment_id."""
        mock_subscription_repo.get_active_by_user.return_value = None
        mock_subscription_repo.get_by_payment_id.return_value = sample_subscription_plan

        result = await subscription_service.activate_subscription(
            user_id=123456,
            plan_type="one_month",
            stars_paid=360,
            payment_id="payment_123",
            current_user_id=999999,
        )

        assert result == sample_subscription_plan
        mock_subscription_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_error_for_invalid_plan_type(
        self, subscription_service, mock_subscription_repo
    ):
        """Verifica que lanza error para tipo de plan inválido."""
        mock_subscription_repo.get_active_by_user.return_value = None
        mock_subscription_repo.get_by_payment_id.return_value = None

        with pytest.raises(ValueError, match="Invalid plan type"):
            await subscription_service.activate_subscription(
                user_id=123456,
                plan_type="invalid_plan",
                stars_paid=360,
                payment_id="payment_new",
                current_user_id=999999,
            )


class TestCancelSubscription:
    """Tests para el método cancel_subscription."""

    @pytest.mark.asyncio
    async def test_cancels_active_subscription(
        self, subscription_service, mock_subscription_repo, sample_subscription_plan
    ):
        """Verifica que cancela una suscripción activa."""
        mock_subscription_repo.get_active_by_user.return_value = sample_subscription_plan

        result = await subscription_service.cancel_subscription(123456, 999999)

        assert result is True
        mock_subscription_repo.deactivate.assert_called_once_with(
            sample_subscription_plan.id, 999999
        )

    @pytest.mark.asyncio
    async def test_returns_false_when_no_subscription(
        self, subscription_service, mock_subscription_repo
    ):
        """Verifica que retorna False cuando no hay suscripción."""
        mock_subscription_repo.get_active_by_user.return_value = None

        result = await subscription_service.cancel_subscription(123456, 999999)

        assert result is False
        mock_subscription_repo.deactivate.assert_not_called()


class TestGetExpiringSubscriptions:
    """Tests para el método get_expiring_subscriptions."""

    @pytest.mark.asyncio
    async def test_returns_expiring_plans(self, subscription_service, mock_subscription_repo):
        """Verifica que retorna planes que expiran pronto."""
        expiring_plans = [
            SubscriptionPlan(
                id=uuid.uuid4(),
                user_id=123456,
                plan_type=PlanType.ONE_MONTH,
                stars_paid=360,
                payment_id="payment_expiring",
                starts_at=datetime.now(UTC) - timedelta(days=27),
                expires_at=datetime.now(UTC) + timedelta(days=2),
                is_active=True,
            )
        ]
        mock_subscription_repo.get_expiring_plans.return_value = expiring_plans

        result = await subscription_service.get_expiring_subscriptions(days=3)

        assert result == expiring_plans
        mock_subscription_repo.get_expiring_plans.assert_called_once_with(3, 0)

    @pytest.mark.asyncio
    async def test_default_days_parameter(self, subscription_service, mock_subscription_repo):
        """Verifica que el parámetro days por defecto es 3."""
        mock_subscription_repo.get_expiring_plans.return_value = []

        await subscription_service.get_expiring_subscriptions()

        mock_subscription_repo.get_expiring_plans.assert_called_once_with(3, 0)


class TestGetExpiredSubscriptions:
    """Tests para el método get_expired_subscriptions."""

    @pytest.mark.asyncio
    async def test_returns_expired_plans(self, subscription_service, mock_subscription_repo):
        """Verifica que retorna planes expirados."""
        expired_plans = [
            SubscriptionPlan(
                id=uuid.uuid4(),
                user_id=123456,
                plan_type=PlanType.ONE_MONTH,
                stars_paid=360,
                payment_id="payment_expired",
                starts_at=datetime.now(UTC) - timedelta(days=60),
                expires_at=datetime.now(UTC) - timedelta(days=30),
                is_active=True,
            )
        ]
        mock_subscription_repo.get_expired_plans.return_value = expired_plans

        result = await subscription_service.get_expired_subscriptions()

        assert result == expired_plans
        mock_subscription_repo.get_expired_plans.assert_called_once_with(0)


class TestGetUserDataLimit:
    """Tests para el método get_user_data_limit."""

    @pytest.mark.asyncio
    async def test_returns_unlimited_for_premium_user(
        self, subscription_service, mock_subscription_repo, sample_subscription_plan
    ):
        """Verifica que retorna -1 (ilimitado) para usuarios premium."""
        mock_subscription_repo.get_active_by_user.return_value = sample_subscription_plan

        result = await subscription_service.get_user_data_limit(123456, 999999)

        assert result == -1  # Unlimited

    @pytest.mark.asyncio
    async def test_returns_default_limit_for_non_premium_user(
        self, subscription_service, mock_subscription_repo
    ):
        """Verifica que retorna 10GB por defecto para usuarios no premium."""
        mock_subscription_repo.get_active_by_user.return_value = None

        result = await subscription_service.get_user_data_limit(123456, 999999)

        assert result == 10737418240  # 10GB en bytes


class TestSubscriptionOption:
    """Tests para la dataclass SubscriptionOption."""

    def test_create_subscription_option(self):
        """Verifica creación de opción de suscripción."""
        option = SubscriptionOption(
            name="Test Plan",
            plan_type=PlanType.ONE_MONTH,
            duration_months=1,
            stars=500,
            usdt=4.99,
        )

        assert option.name == "Test Plan"
        assert option.plan_type == PlanType.ONE_MONTH
        assert option.duration_months == 1
        assert option.stars == 500
        assert option.usdt == 4.99
        assert option.data_limit == "Unlimited"
        assert option.bonus_percent == 0

    def test_create_subscription_option_with_all_fields(self):
        """Verifica creación con todos los campos."""
        option = SubscriptionOption(
            name="Test Plan",
            plan_type=PlanType.THREE_MONTHS,
            duration_months=3,
            stars=1000,
            usdt=9.99,
            data_limit="100GB",
            bonus_percent=15,
        )

        assert option.data_limit == "100GB"
        assert option.bonus_percent == 15


class TestSubscriptionConstants:
    """Tests para constantes de suscripción."""

    def test_subscription_options_count(self):
        """Verifica cantidad de opciones de suscripción."""
        assert len(SUBSCRIPTION_OPTIONS) == 3

    def test_subscription_options_have_unique_plan_types(self):
        """Verifica que las opciones tienen tipos de plan únicos."""
        plan_types = [option.plan_type for option in SUBSCRIPTION_OPTIONS]
        assert len(plan_types) == len(set(plan_types))

    def test_subscription_options_have_bonus_for_longer_plans(self):
        """Verifica que planes más largos tienen bonus."""
        one_month = next(o for o in SUBSCRIPTION_OPTIONS if o.plan_type == PlanType.ONE_MONTH)
        three_months = next(o for o in SUBSCRIPTION_OPTIONS if o.plan_type == PlanType.THREE_MONTHS)
        six_months = next(o for o in SUBSCRIPTION_OPTIONS if o.plan_type == PlanType.SIX_MONTHS)

        assert one_month.bonus_percent == 0
        assert three_months.bonus_percent > 0
        assert six_months.bonus_percent > three_months.bonus_percent
