"""Tests de integración para los endpoints de paquetes de datos."""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_package_options(client: AsyncClient):
    """Test obtener opciones de paquetes."""
    response = await client.get("/api/v1/data-packages/options")
    assert response.status_code == status.HTTP_200_OK
    options = response.json()
    assert len(options) > 0
    assert options[0]["package_type"] == "basic"


@pytest.mark.asyncio
async def test_get_my_packages(client: AsyncClient, auth_headers: dict):
    """Test obtener mis paquetes."""
    response = await client.get("/api/v1/data-packages/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "packages" in data
    assert data["total_count"] == 0


@pytest.mark.asyncio
async def test_purchase_package_integration(client: AsyncClient, auth_headers: dict):
    """Test flujo completo de compra de un paquete."""
    purchase_data = {
        "package_type": "basic",
        "telegram_payment_id": "test_pay_id",
        "is_referred_first_purchase": False,
    }

    response = await client.post(
        "/api/v1/data-packages/purchase", json=purchase_data, headers=auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["package"]["package_type"] == "basic"
    assert data["package"]["telegram_payment_id"] == "test_pay_id"
    assert "bonuses" in data

    # Verificar que ahora aparece en "me"
    response_me = await client.get("/api/v1/data-packages/me", headers=auth_headers)
    assert response_me.json()["total_count"] == 1
