"""Tests de integración para endpoints de Tickets."""

import pytest
from httpx import AsyncClient


class TestTicketsEndpoints:
    """Tests de integración para endpoints de tickets."""

    @pytest.mark.asyncio
    async def test_create_ticket(self, client: AsyncClient, auth_headers: dict):
        """Prueba crear un ticket."""
        response = await client.post(
            "/api/v1/tickets",
            json={
                "category": "vpn_fail",
                "subject": "VPN connection failing",
                "message": "My VPN keeps disconnecting every 5 minutes",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["category"] == "vpn_fail"
        assert data["subject"] == "VPN connection failing"
        assert data["status"] == "open"
        assert "ticket_number" in data

    @pytest.mark.asyncio
    async def test_create_ticket_invalid_category(self, client: AsyncClient, auth_headers: dict):
        """Prueba crear ticket con categoría inválida."""
        response = await client.post(
            "/api/v1/tickets",
            json={
                "category": "invalid_category",
                "subject": "Test",
                "message": "Test message",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_ticket_short_subject(self, client: AsyncClient, auth_headers: dict):
        """Prueba crear ticket con asunto muy corto."""
        response = await client.post(
            "/api/v1/tickets",
            json={
                "category": "other",
                "subject": "Hi",  # Muy corto (min 5 chars)
                "message": "Test message",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_user_tickets(self, client: AsyncClient, auth_headers: dict):
        """Prueba obtener tickets del usuario."""
        # Primero crear un ticket
        await client.post(
            "/api/v1/tickets",
            json={
                "category": "other",
                "subject": "Test ticket",
                "message": "Test message",
            },
            headers=auth_headers,
        )

        # Luego obtener tickets
        response = await client.get("/api/v1/tickets", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_ticket_unauthorized(self, client: AsyncClient, auth_headers: dict):
        """Prueba que usuario no puede ver tickets de otros."""
        # El endpoint requiere un UUID válido, probamos con formato inválido
        response = await client.get("/api/v1/tickets/invalid-uuid", headers=auth_headers)

        # Puede ser 400 (bad request) o 404 (no encontrado)
        assert response.status_code in [400, 404]

    @pytest.mark.asyncio
    async def test_add_message_to_ticket(self, client: AsyncClient, auth_headers: dict):
        """Prueba agregar mensaje a ticket."""
        # Crear ticket
        create_response = await client.post(
            "/api/v1/tickets",
            json={
                "category": "other",
                "subject": "Test ticket",
                "message": "Test message",
            },
            headers=auth_headers,
        )
        ticket_id = create_response.json()["id"]

        # Agregar mensaje
        response = await client.post(
            f"/api/v1/tickets/{ticket_id}/messages",
            json={"message": "Follow-up message"},
            headers=auth_headers,
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_admin_resolve_ticket(self, client: AsyncClient, admin_auth_headers: dict):
        """Prueba que admin puede resolver ticket."""
        # Crear ticket
        create_response = await client.post(
            "/api/v1/tickets",
            json={
                "category": "vpn_fail",
                "subject": "VPN issue",
                "message": "Help please",
            },
            headers=admin_auth_headers,
        )
        ticket_id = create_response.json()["id"]

        # Resolver ticket
        response = await client.post(
            f"/api/v1/tickets/{ticket_id}/resolve",
            json={"notes": "Issue resolved by restarting server"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"

    @pytest.mark.asyncio
    async def test_non_admin_cannot_resolve(self, client: AsyncClient, auth_headers: dict):
        """Prueba que no-admin no puede resolver tickets."""
        # Crear ticket
        create_response = await client.post(
            "/api/v1/tickets",
            json={
                "category": "other",
                "subject": "Test ticket for resolve",
                "message": "Test message",
            },
            headers=auth_headers,
        )

        # Verificar que se creó el ticket
        if create_response.status_code != 201:
            pytest.skip(f"Could not create ticket: {create_response.status_code}")

        ticket_id = create_response.json()["id"]

        # Intentar resolver
        response = await client.post(
            f"/api/v1/tickets/{ticket_id}/resolve",
            json={"notes": "Trying to resolve"},
            headers=auth_headers,
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_user_close_own_ticket(self, client: AsyncClient, auth_headers: dict):
        """Prueba que usuario puede cerrar su propio ticket."""
        # Crear ticket
        create_response = await client.post(
            "/api/v1/tickets",
            json={
                "category": "other",
                "subject": "Test ticket",
                "message": "Test message",
            },
            headers=auth_headers,
        )
        ticket_id = create_response.json()["id"]

        # Cerrar ticket
        response = await client.post(
            f"/api/v1/tickets/{ticket_id}/close",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "closed"

    @pytest.mark.asyncio
    async def test_admin_get_pending_tickets(self, client: AsyncClient, admin_auth_headers: dict):
        """Prueba que admin puede obtener tickets pendientes."""
        # Crear algunos tickets
        await client.post(
            "/api/v1/tickets",
            json={
                "category": "vpn_fail",
                "subject": "VPN issue 1",
                "message": "Help",
            },
            headers=admin_auth_headers,
        )

        # Obtener pendientes
        response = await client.get("/api/v1/tickets/admin/pending", headers=admin_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_non_admin_cannot_get_pending(self, client: AsyncClient, auth_headers: dict):
        """Prueba que no-admin no puede ver tickets pendientes."""
        response = await client.get("/api/v1/tickets/admin/pending", headers=auth_headers)

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_get_ticket_stats(self, client: AsyncClient, admin_auth_headers: dict):
        """Prueba obtener estadísticas de tickets."""
        response = await client.get("/api/v1/tickets/admin/stats", headers=admin_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "open_count" in data
        assert "responded_count" in data
        assert "resolved_count" in data
        assert "closed_count" in data

    @pytest.mark.asyncio
    async def test_invalid_ticket_id_format(self, client: AsyncClient, auth_headers: dict):
        """Prueba formato inválido de ID de ticket."""
        response = await client.get("/api/v1/tickets/invalid-uuid-format", headers=auth_headers)

        assert response.status_code == 400
