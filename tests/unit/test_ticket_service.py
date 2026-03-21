"""Tests unitarios para TicketService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities import (
    Ticket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
)

from src.core.application.services.ticket_service import TicketService
from src.infrastructure.persistence.repositories.ticket_repository import TicketRepository


@pytest.fixture
async def ticket_service(test_session: AsyncSession) -> TicketService:
    """Crea el servicio de tickets."""
    repo = TicketRepository(test_session)
    return TicketService(repo)


@pytest.fixture
async def test_ticket(test_session: AsyncSession, ticket_service: TicketService) -> Ticket:
    """Crea un ticket de test."""
    return await ticket_service.create_ticket(
        user_id=123456,
        category=TicketCategory.VPN_FAIL,
        subject="Test ticket",
        message="Test message",
    )


class TestTicketService:
    """Tests para TicketService."""

    @pytest.mark.asyncio
    async def test_create_ticket(self, ticket_service: TicketService):
        """Prueba crear un ticket."""
        ticket = await ticket_service.create_ticket(
            user_id=123456,
            category=TicketCategory.PAYMENT,
            subject="Payment issue",
            message="I have a payment problem",
        )

        assert ticket is not None
        assert ticket.user_id == 123456
        assert ticket.category == TicketCategory.PAYMENT
        assert ticket.priority == TicketPriority.MEDIUM  # Auto-assigned by category
        assert ticket.status == TicketStatus.OPEN
        assert ticket.subject == "Payment issue"

    @pytest.mark.asyncio
    async def test_create_ticket_auto_priority(self, ticket_service: TicketService):
        """Prueba que la prioridad se asigna automáticamente según categoría."""
        vpn_ticket = await ticket_service.create_ticket(
            user_id=123456,
            category=TicketCategory.VPN_FAIL,
            subject="VPN not working",
            message="Help",
        )
        other_ticket = await ticket_service.create_ticket(
            user_id=123456,
            category=TicketCategory.OTHER,
            subject="Question",
            message="Quick question",
        )

        assert vpn_ticket.priority == TicketPriority.HIGH
        assert other_ticket.priority == TicketPriority.LOW

    @pytest.mark.asyncio
    async def test_get_user_tickets(self, ticket_service: TicketService, test_ticket: Ticket):
        """Prueba obtener tickets de usuario."""
        await ticket_service.create_ticket(
            user_id=123456,
            category=TicketCategory.OTHER,
            subject="Another ticket",
            message="Another message",
        )

        tickets = await ticket_service.get_user_tickets(123456)

        assert len(tickets) == 2
        assert all(t.user_id == 123456 for t in tickets)

    @pytest.mark.asyncio
    async def test_get_ticket_with_messages(
        self, ticket_service: TicketService, test_ticket: Ticket
    ):
        """Prueba obtener ticket con mensajes."""
        result = await ticket_service.get_ticket_with_messages(test_ticket.id)

        assert result is not None
        ticket, messages = result
        assert ticket.id == test_ticket.id
        assert len(messages) >= 1  # Al menos el mensaje inicial

    @pytest.mark.asyncio
    async def test_add_user_message(self, ticket_service: TicketService, test_ticket: Ticket):
        """Prueba agregar mensaje de usuario."""
        message = await ticket_service.add_user_message(
            test_ticket.id,
            123456,
            "Follow-up message",
        )

        assert message is not None
        assert message.message == "Follow-up message"
        assert message.from_admin is False

    @pytest.mark.asyncio
    async def test_add_user_message_reopens_ticket(
        self, ticket_service: TicketService, test_ticket: Ticket
    ):
        """Prueba que mensaje de usuario reabre ticket respondido."""
        # Primero responder el ticket
        await ticket_service.add_admin_response(test_ticket.id, 999999, "Admin response")

        # Usuario responde
        await ticket_service.add_user_message(test_ticket.id, 123456, "Thanks!")

        ticket_result = await ticket_service.get_ticket_with_messages(test_ticket.id)
        assert ticket_result is not None
        ticket, _ = ticket_result
        assert ticket.status == TicketStatus.OPEN

    @pytest.mark.asyncio
    async def test_add_admin_response(self, ticket_service: TicketService, test_ticket: Ticket):
        """Prueba agregar respuesta de admin."""
        message = await ticket_service.add_admin_response(
            test_ticket.id,
            999999,
            "We are looking into it",
        )

        assert message is not None
        assert message.message == "We are looking into it"
        assert message.from_admin is True

    @pytest.mark.asyncio
    async def test_add_admin_response_updates_status(
        self, ticket_service: TicketService, test_ticket: Ticket
    ):
        """Prueba que respuesta de admin actualiza estado a RESPONDED."""
        await ticket_service.add_admin_response(test_ticket.id, 999999, "Response")

        ticket_result = await ticket_service.get_ticket_with_messages(test_ticket.id)
        assert ticket_result is not None
        ticket, _ = ticket_result
        assert ticket.status == TicketStatus.RESPONDED

    @pytest.mark.asyncio
    async def test_resolve_ticket(self, ticket_service: TicketService, test_ticket: Ticket):
        """Prueba resolver ticket."""
        resolved = await ticket_service.resolve_ticket(
            test_ticket.id,
            999999,
            "Issue resolved",
        )

        assert resolved is not None
        assert resolved.status == TicketStatus.RESOLVED
        assert resolved.resolved_by == 999999
        assert resolved.admin_notes == "Issue resolved"

    @pytest.mark.asyncio
    async def test_close_ticket_by_user(self, ticket_service: TicketService, test_ticket: Ticket):
        """Prueba cerrar ticket por usuario."""
        closed = await ticket_service.close_ticket(
            test_ticket.id,
            123456,
            is_admin=False,
        )

        assert closed is not None
        assert closed.status == TicketStatus.CLOSED

    @pytest.mark.asyncio
    async def test_close_ticket_by_admin(self, ticket_service: TicketService, test_ticket: Ticket):
        """Prueba cerrar ticket por admin."""
        closed = await ticket_service.close_ticket(
            test_ticket.id,
            999999,
            is_admin=True,
        )

        assert closed is not None
        assert closed.status == TicketStatus.CLOSED

    @pytest.mark.asyncio
    async def test_user_cannot_close_others_ticket(
        self, ticket_service: TicketService, test_ticket: Ticket
    ):
        """Prueba que usuario no puede cerrar ticket de otro."""
        closed = await ticket_service.close_ticket(
            test_ticket.id,
            999888,  # Different user
            is_admin=False,
        )

        assert closed is None

    @pytest.mark.asyncio
    async def test_reopen_ticket(self, ticket_service: TicketService, test_ticket: Ticket):
        """Prueba reabre ticket cerrado."""
        # Cerrar ticket
        await ticket_service.close_ticket(test_ticket.id, 123456, is_admin=False)

        # Reabrir
        reopened = await ticket_service.reopen_ticket(test_ticket.id, 999999)

        assert reopened is not None
        assert reopened.status == TicketStatus.OPEN

    @pytest.mark.asyncio
    async def test_reopen_non_closed_ticket(
        self, ticket_service: TicketService, test_ticket: Ticket
    ):
        """Prueba que no se puede reabre ticket no cerrado."""
        reopened = await ticket_service.reopen_ticket(test_ticket.id, 999999)

        assert reopened is None  # No se puede reabre porque está OPEN

    @pytest.mark.asyncio
    async def test_get_pending_tickets(self, ticket_service: TicketService, test_ticket: Ticket):
        """Prueba obtener tickets pendientes."""
        pending = await ticket_service.get_pending_tickets()

        assert len(pending) >= 1
        assert all(t.status in [TicketStatus.OPEN, TicketStatus.RESPONDED] for t in pending)

    @pytest.mark.asyncio
    async def test_count_open_tickets(self, ticket_service: TicketService, test_ticket: Ticket):
        """Prueba contar tickets abiertos."""
        count = await ticket_service.count_open_tickets()

        assert count >= 1
