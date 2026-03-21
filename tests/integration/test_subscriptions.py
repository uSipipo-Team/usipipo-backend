"""Tests de integración para Suscripciones."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from usipipo_commons.domain.entities.subscription_plan import (
    PlanType,
    SubscriptionPlan,
)


@pytest.mark.asyncio
async def test_list_plans_does_not_require_auth(client: AsyncClient):
    """Test que listar planes no requiere autenticación."""
    response = await client.get("/api/v1/subscriptions/plans")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_plans_returns_all_plans(client: AsyncClient):
    """Test que listar planes retorna todos los planes disponibles."""
    response = await client.get("/api/v1/subscriptions/plans")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3

    # Verificar estructura de cada plan
    for plan in data:
        assert "name" in plan
        assert "plan_type" in plan
        assert "duration_months" in plan
        assert "stars" in plan
        assert "usdt" in plan
        assert "data_limit" in plan
        assert "bonus_percent" in plan

    # Verificar planes específicos
    plan_names = [p["name"] for p in data]
    assert "1 Month" in plan_names
    assert "3 Months" in plan_names
    assert "6 Months" in plan_names


@pytest.mark.asyncio
async def test_list_plans_has_correct_bonus_structure(client: AsyncClient):
    """Test que los planes tienen la estructura de bonus correcta."""
    response = await client.get("/api/v1/subscriptions/plans")
    assert response.status_code == 200

    data = response.json()

    # 1 Month no tiene bonus
    one_month = next(p for p in data if p["name"] == "1 Month")
    assert one_month["bonus_percent"] == 0

    # 3 Months tiene bonus
    three_months = next(p for p in data if p["name"] == "3 Months")
    assert three_months["bonus_percent"] > 0

    # 6 Months tiene más bonus que 3 Months
    six_months = next(p for p in data if p["name"] == "6 Months")
    assert six_months["bonus_percent"] > three_months["bonus_percent"]


@pytest.mark.asyncio
async def test_activate_subscription_requires_auth(client: AsyncClient):
    """Test que activar suscripción requiere autenticación."""
    payload = {
        "plan_type": "one_month",
        "payment_id": "payment_test_123",
    }
    response = await client.post("/api/v1/subscriptions/activate", json=payload)
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_activate_subscription_invalid_plan_type(client: AsyncClient, auth_headers: dict):
    """Test de activar suscripción con tipo de plan inválido."""
    payload = {
        "plan_type": "invalid_plan",
        "payment_id": "payment_test_123",
    }
    response = await client.post(
        "/api/v1/subscriptions/activate",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 400  # Bad request
    assert "Invalid plan type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_activate_subscription_missing_fields(client: AsyncClient, auth_headers: dict):
    """Test de activar suscripción con campos faltantes."""
    payload = {
        "plan_type": "one_month",
        # payment_id faltante
    }
    response = await client.post(
        "/api/v1/subscriptions/activate",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_activate_subscription_success(client: AsyncClient, auth_headers: dict):
    """Test de activación exitosa de suscripción."""
    payload = {
        "plan_type": "one_month",
        "payment_id": "payment_test_success",
    }

    # Mock para evitar acceso a base de datos real
    mock_subscription = SubscriptionPlan(
        id=uuid4(),
        user_id=123456,
        plan_type=PlanType.ONE_MONTH,
        stars_paid=360,
        payment_id="payment_test_success",
        starts_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=30),
        is_active=True,
    )

    with patch(
        "src.core.application.services.subscription_service.SubscriptionService.activate_subscription",
        new_callable=AsyncMock,
        return_value=mock_subscription,
    ):
        response = await client.post(
            "/api/v1/subscriptions/activate",
            json=payload,
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "subscription_id" in data
    assert data["plan_type"] == "one_month"
    assert "expires_at" in data
    assert "message" in data


@pytest.mark.asyncio
async def test_activate_subscription_duplicate_payment_id(client: AsyncClient, auth_headers: dict):
    """Test de activación con payment_id duplicado (idempotencia)."""
    payload = {
        "plan_type": "one_month",
        "payment_id": "payment_duplicate",
    }

    # Mock que simula suscripción existente por payment_id
    mock_subscription = SubscriptionPlan(
        id=uuid4(),
        user_id=123456,
        plan_type=PlanType.ONE_MONTH,
        stars_paid=360,
        payment_id="payment_duplicate",
        starts_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=30),
        is_active=True,
    )

    with patch(
        "src.core.application.services.subscription_service.SubscriptionService.activate_subscription",
        new_callable=AsyncMock,
        return_value=mock_subscription,
    ):
        response = await client.post(
            "/api/v1/subscriptions/activate",
            json=payload,
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_activate_subscription_existing_active(client: AsyncClient, auth_headers: dict):
    """Test de activación cuando ya existe suscripción activa."""
    payload = {
        "plan_type": "three_months",
        "payment_id": "payment_new_123",
    }

    # Mock que lanza error por suscripción activa existente
    with patch(
        "src.core.application.services.subscription_service.SubscriptionService.activate_subscription",
        new_callable=AsyncMock,
        side_effect=ValueError("User already has an active subscription"),
    ):
        response = await client.post(
            "/api/v1/subscriptions/activate",
            json=payload,
            headers=auth_headers,
        )

    assert response.status_code == 400
    assert "already has an active subscription" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_subscription_requires_auth(client: AsyncClient):
    """Test que obtener suscripción actual requiere autenticación."""
    response = await client.get("/api/v1/subscriptions/me")
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_get_user_subscription_no_subscription(client: AsyncClient, auth_headers: dict):
    """Test de obtener suscripción cuando no hay suscripción activa."""
    with patch(
        "src.core.application.services.subscription_service.SubscriptionService.get_user_subscription",
        new_callable=AsyncMock,
        return_value=None,
    ):
        response = await client.get(
            "/api/v1/subscriptions/me",
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.asyncio
async def test_get_user_subscription_with_active_subscription(
    client: AsyncClient, auth_headers: dict
):
    """Test de obtener suscripción activa."""
    mock_subscription = SubscriptionPlan(
        id=uuid4(),
        user_id=123456,
        plan_type=PlanType.THREE_MONTHS,
        stars_paid=960,
        payment_id="payment_active_123",
        starts_at=datetime.now(UTC) - timedelta(days=10),
        expires_at=datetime.now(UTC) + timedelta(days=80),
        is_active=True,
    )

    with patch(
        "src.core.application.services.subscription_service.SubscriptionService.get_user_subscription",
        new_callable=AsyncMock,
        return_value=mock_subscription,
    ):
        response = await client.get(
            "/api/v1/subscriptions/me",
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data is not None
    assert "id" in data
    assert data["user_id"] == 123456
    assert data["plan_type"] == "three_months"
    assert data["stars_paid"] == 960
    assert data["is_active"] is True
    assert "days_remaining" in data
    assert "is_expiring_soon" in data
    assert "is_expired" in data


@pytest.mark.asyncio
async def test_get_user_subscription_expiring_soon(client: AsyncClient, auth_headers: dict):
    """Test de obtener suscripción que expira pronto."""
    mock_subscription = SubscriptionPlan(
        id=uuid4(),
        user_id=123456,
        plan_type=PlanType.ONE_MONTH,
        stars_paid=360,
        payment_id="payment_expiring",
        starts_at=datetime.now(UTC) - timedelta(days=28),
        expires_at=datetime.now(UTC) + timedelta(days=2),
        is_active=True,
    )

    with patch(
        "src.core.application.services.subscription_service.SubscriptionService.get_user_subscription",
        new_callable=AsyncMock,
        return_value=mock_subscription,
    ):
        response = await client.get(
            "/api/v1/subscriptions/me",
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["is_expiring_soon"] is True
    assert data["days_remaining"] <= 3


@pytest.mark.asyncio
async def test_get_user_subscription_expired(client: AsyncClient, auth_headers: dict):
    """Test de obtener suscripción expirada."""
    mock_subscription = SubscriptionPlan(
        id=uuid4(),
        user_id=123456,
        plan_type=PlanType.ONE_MONTH,
        stars_paid=360,
        payment_id="payment_expired",
        starts_at=datetime.now(UTC) - timedelta(days=60),
        expires_at=datetime.now(UTC) - timedelta(days=30),
        is_active=True,
    )

    with patch(
        "src.core.application.services.subscription_service.SubscriptionService.get_user_subscription",
        new_callable=AsyncMock,
        return_value=mock_subscription,
    ):
        response = await client.get(
            "/api/v1/subscriptions/me",
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["is_expired"] is True
    assert data["days_remaining"] == 0
