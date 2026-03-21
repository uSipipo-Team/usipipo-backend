"""Tests unitarios para TicketRepository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities import (
    Ticket,
    TicketCategory,
    TicketMessage,
    TicketPriority,
    TicketStatus,
)

from src.infrastructure.persistence.models.user_model import UserModel
from src.infrastructure.persistence.repositories.ticket_repository import TicketRepository


@pytest.fixture
async def ticket_repository(test_session: AsyncSession) -> TicketRepository:
    """Crea el repositorio de tickets."""
    return TicketRepository(test_session)


@pytest.fixture
async def test_user(test_session: AsyncSession) -> UserModel:
    """Crea un usuario de test."""
    user = UserModel(
        telegram_id=123456,
        username="testuser",
        first_name="Test",
        last_name="User",
        is_admin=False,
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="ref_test",
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


class TestTicketRepository:
    """Tests para TicketRepository."""

    @pytest.mark.asyncio
    async def test_save_ticket(self, ticket_repository: TicketRepository, test_user: UserModel):
        """Prueba guardar un ticket."""
        ticket = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.VPN_FAIL,
            priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN,
            subject="Test ticket",
        )

        saved = await ticket_repository.save(ticket)

        assert saved.id == ticket.id
        assert saved.user_id == test_user.telegram_id
        assert saved.category == TicketCategory.VPN_FAIL
        assert saved.priority == TicketPriority.HIGH
        assert saved.status == TicketStatus.OPEN

    @pytest.mark.asyncio
    async def test_get_by_id(self, ticket_repository: TicketRepository, test_user: UserModel):
        """Prueba obtener ticket por ID."""
        ticket = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.PAYMENT,
            priority=TicketPriority.MEDIUM,
            subject="Payment issue",
        )
        await ticket_repository.save(ticket)

        retrieved = await ticket_repository.get_by_id(ticket.id)

        assert retrieved is not None
        assert retrieved.id == ticket.id
        assert retrieved.subject == "Payment issue"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, ticket_repository: TicketRepository):
        """Prueba obtener ticket inexistente."""
        from uuid import uuid4

        retrieved = await ticket_repository.get_by_id(uuid4())

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_by_user(self, ticket_repository: TicketRepository, test_user: UserModel):
        """Prueba obtener tickets por usuario."""
        ticket1 = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.VPN_FAIL,
            priority=TicketPriority.HIGH,
            subject="Ticket 1",
        )
        ticket2 = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.OTHER,
            priority=TicketPriority.LOW,
            subject="Ticket 2",
        )
        await ticket_repository.save(ticket1)
        await ticket_repository.save(ticket2)

        tickets = await ticket_repository.get_by_user(test_user.telegram_id)

        assert len(tickets) == 2
        assert all(t.user_id == test_user.telegram_id for t in tickets)

    @pytest.mark.asyncio
    async def test_update_ticket(self, ticket_repository: TicketRepository, test_user: UserModel):
        """Prueba actualizar ticket."""
        ticket = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.ACCOUNT,
            priority=TicketPriority.LOW,
            subject="Original subject",
        )
        await ticket_repository.save(ticket)

        ticket.subject = "Updated subject"
        ticket.status = TicketStatus.RESPONDED

        updated = await ticket_repository.update(ticket)

        assert updated.subject == "Updated subject"
        assert updated.status == TicketStatus.RESPONDED

    @pytest.mark.asyncio
    async def test_get_by_status(self, ticket_repository: TicketRepository, test_user: UserModel):
        """Prueba obtener tickets por estado."""
        ticket1 = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.VPN_FAIL,
            priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN,
            subject="Open ticket",
        )
        ticket2 = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.OTHER,
            priority=TicketPriority.LOW,
            status=TicketStatus.CLOSED,
            subject="Closed ticket",
        )
        await ticket_repository.save(ticket1)
        await ticket_repository.save(ticket2)

        open_tickets = await ticket_repository.get_by_status(TicketStatus.OPEN)

        assert len(open_tickets) == 1
        assert open_tickets[0].status == TicketStatus.OPEN

    @pytest.mark.asyncio
    async def test_get_all_open(self, ticket_repository: TicketRepository, test_user: UserModel):
        """Prueba obtener todos los tickets abiertos."""
        ticket1 = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.VPN_FAIL,
            priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN,
            subject="Open ticket",
        )
        ticket2 = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.OTHER,
            priority=TicketPriority.LOW,
            status=TicketStatus.RESPONDED,
            subject="Responded ticket",
        )
        ticket3 = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.PAYMENT,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.CLOSED,
            subject="Closed ticket",
        )
        await ticket_repository.save(ticket1)
        await ticket_repository.save(ticket2)
        await ticket_repository.save(ticket3)

        open_tickets = await ticket_repository.get_all_open()

        assert len(open_tickets) == 2
        assert all(t.status in [TicketStatus.OPEN, TicketStatus.RESPONDED] for t in open_tickets)

    @pytest.mark.asyncio
    async def test_save_message(self, ticket_repository: TicketRepository, test_user: UserModel):
        """Prueba guardar mensaje de ticket."""
        ticket = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.VPN_FAIL,
            priority=TicketPriority.HIGH,
            subject="Test ticket",
        )
        await ticket_repository.save(ticket)

        message = TicketMessage(
            ticket_id=ticket.id,
            from_user_id=test_user.telegram_id,
            message="Test message",
            from_admin=False,
        )

        saved_message = await ticket_repository.save_message(message)

        assert saved_message.id == message.id
        assert saved_message.ticket_id == ticket.id
        assert saved_message.message == "Test message"

    @pytest.mark.asyncio
    async def test_get_messages(self, ticket_repository: TicketRepository, test_user: UserModel):
        """Prueba obtener mensajes de ticket."""
        ticket = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.VPN_FAIL,
            priority=TicketPriority.HIGH,
            subject="Test ticket",
        )
        await ticket_repository.save(ticket)

        message1 = TicketMessage(
            ticket_id=ticket.id,
            from_user_id=test_user.telegram_id,
            message="Message 1",
            from_admin=False,
        )
        message2 = TicketMessage(
            ticket_id=ticket.id,
            from_user_id=999999,
            message="Message 2",
            from_admin=True,
        )
        await ticket_repository.save_message(message1)
        await ticket_repository.save_message(message2)

        messages = await ticket_repository.get_messages(ticket.id)

        assert len(messages) == 2
        assert messages[0].message == "Message 1"
        assert messages[1].message == "Message 2"

    @pytest.mark.asyncio
    async def test_count_open(self, ticket_repository: TicketRepository, test_user: UserModel):
        """Prueba contar tickets abiertos."""
        ticket1 = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.VPN_FAIL,
            priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN,
            subject="Open ticket 1",
        )
        ticket2 = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.OTHER,
            priority=TicketPriority.LOW,
            status=TicketStatus.RESPONDED,
            subject="Responded ticket",
        )
        ticket3 = Ticket(
            user_id=test_user.telegram_id,
            category=TicketCategory.PAYMENT,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.CLOSED,
            subject="Closed ticket",
        )
        await ticket_repository.save(ticket1)
        await ticket_repository.save(ticket2)
        await ticket_repository.save(ticket3)

        count = await ticket_repository.count_open()

        assert count == 2
