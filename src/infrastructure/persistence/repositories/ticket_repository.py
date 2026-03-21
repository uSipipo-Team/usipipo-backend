"""Ticket repository implementation with SQLAlchemy."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities import (
    Ticket,
    TicketCategory,
    TicketMessage,
    TicketPriority,
    TicketStatus,
)

from src.core.domain.interfaces.i_ticket_repository import ITicketRepository
from src.infrastructure.persistence.models.ticket_message_model import TicketMessageModel
from src.infrastructure.persistence.models.ticket_model import TicketModel


class TicketRepository(ITicketRepository):
    """PostgreSQL implementation of ticket repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: TicketModel) -> Ticket:
        """Converts model to entity."""
        return Ticket(
            id=model.id,
            user_id=model.user_id,
            category=TicketCategory(model.category),
            priority=TicketPriority(model.priority),
            status=TicketStatus(model.status),
            subject=model.subject,
            created_at=model.created_at,
            updated_at=model.updated_at,
            resolved_at=model.resolved_at,
            resolved_by=model.resolved_by,
            admin_notes=model.admin_notes,
        )

    def _to_message_entity(self, model: TicketMessageModel) -> TicketMessage:
        """Converts message model to entity."""
        return TicketMessage(
            id=model.id,
            ticket_id=model.ticket_id,
            from_user_id=model.from_user_id,
            message=model.message,
            from_admin=model.from_admin,
            created_at=model.created_at,
        )

    async def save(self, ticket: Ticket) -> Ticket:
        """Saves a new ticket."""
        model = TicketModel(
            id=ticket.id,
            user_id=ticket.user_id,
            category=ticket.category.value,
            priority=ticket.priority.value,
            status=ticket.status.value,
            subject=ticket.subject,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            resolved_at=ticket.resolved_at,
            resolved_by=ticket.resolved_by,
            admin_notes=ticket.admin_notes,
        )
        self.session.add(model)
        await self.session.commit()
        return ticket

    async def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        """Gets a ticket by its ID."""
        result = await self.session.execute(select(TicketModel).where(TicketModel.id == ticket_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_simple_id(self, simple_id: int) -> Ticket | None:
        """Gets a ticket by its simplified ID (int)."""
        result = await self.session.execute(
            select(TicketModel)
            .where((func.abs(TicketModel.id.int_value) % 100000000) == simple_id)
            .order_by(TicketModel.created_at.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user(self, user_id: int) -> list[Ticket]:
        """Gets all tickets from a user."""
        result = await self.session.execute(
            select(TicketModel)
            .where(TicketModel.user_id == user_id)
            .order_by(TicketModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, ticket: Ticket) -> Ticket:
        """Updates an existing ticket."""
        result = await self.session.execute(select(TicketModel).where(TicketModel.id == ticket.id))
        model = result.scalar_one()

        model.category = ticket.category.value
        model.priority = ticket.priority.value
        model.status = ticket.status.value
        model.subject = ticket.subject
        model.updated_at = ticket.updated_at
        model.resolved_at = ticket.resolved_at
        model.resolved_by = ticket.resolved_by
        model.admin_notes = ticket.admin_notes

        await self.session.commit()
        return ticket

    async def get_by_status(self, status: TicketStatus) -> list[Ticket]:
        """Gets tickets by status."""
        result = await self.session.execute(
            select(TicketModel)
            .where(TicketModel.status == status.value)
            .order_by(TicketModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_category(self, category: TicketCategory) -> list[Ticket]:
        """Gets tickets by category."""
        result = await self.session.execute(
            select(TicketModel)
            .where(TicketModel.category == category.value)
            .order_by(TicketModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_all_open(self) -> list[Ticket]:
        """Gets all open tickets (OPEN or RESPONDED)."""
        result = await self.session.execute(
            select(TicketModel)
            .where(TicketModel.status.in_(["open", "responded"]))
            .order_by(
                TicketModel.priority.desc(),  # HIGH first
                TicketModel.created_at.asc(),  # Oldest first
            )
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save_message(self, message: TicketMessage) -> TicketMessage:
        """Saves a ticket message."""
        model = TicketMessageModel(
            id=message.id,
            ticket_id=message.ticket_id,
            from_user_id=message.from_user_id,
            message=message.message,
            from_admin=message.from_admin,
            created_at=message.created_at,
        )
        self.session.add(model)
        await self.session.commit()
        return message

    async def get_messages(self, ticket_id: UUID) -> list[TicketMessage]:
        """Gets all messages from a ticket."""
        result = await self.session.execute(
            select(TicketMessageModel)
            .where(TicketMessageModel.ticket_id == ticket_id)
            .order_by(TicketMessageModel.created_at.asc())
        )
        return [self._to_message_entity(m) for m in result.scalars().all()]

    async def count_open(self) -> int:
        """Counts open tickets."""
        result = await self.session.execute(
            select(func.count())
            .select_from(TicketModel)
            .where(TicketModel.status.in_(["open", "responded"]))
        )
        return result.scalar() or 0
