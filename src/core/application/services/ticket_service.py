"""Ticket service for support ticket management."""

import logging
from uuid import UUID

from usipipo_commons.domain.entities import (
    Ticket,
    TicketCategory,
    TicketMessage,
    TicketPriority,
    TicketStatus,
)

from src.core.domain.interfaces.i_ticket_repository import ITicketRepository

logger = logging.getLogger(__name__)


class TicketService:
    """Service for support ticket management."""

    # Category to priority mapping
    CATEGORY_PRIORITY = {
        TicketCategory.VPN_FAIL: TicketPriority.HIGH,
        TicketCategory.PAYMENT: TicketPriority.MEDIUM,
        TicketCategory.ACCOUNT: TicketPriority.LOW,
        TicketCategory.OTHER: TicketPriority.LOW,
    }

    def __init__(self, ticket_repo: ITicketRepository):
        self.ticket_repo = ticket_repo

    def _get_priority_for_category(self, category: TicketCategory) -> TicketPriority:
        """Determines automatic priority based on category."""
        return self.CATEGORY_PRIORITY.get(category, TicketPriority.LOW)

    async def create_ticket(
        self, user_id: int, category: TicketCategory, subject: str, message: str
    ) -> Ticket:
        """Creates a new support ticket."""
        priority = self._get_priority_for_category(category)

        ticket = Ticket(user_id=user_id, category=category, priority=priority, subject=subject)

        saved_ticket = await self.ticket_repo.save(ticket)
        logger.info(f"Ticket created: {saved_ticket.ticket_number} by user {user_id}")

        # Add initial message
        ticket_message = TicketMessage(
            ticket_id=saved_ticket.id,
            from_user_id=user_id,
            message=message,
            from_admin=False,
        )
        await self.ticket_repo.save_message(ticket_message)

        return saved_ticket

    async def get_user_tickets(self, user_id: int) -> list[Ticket]:
        """Gets user's tickets ordered by date."""
        return await self.ticket_repo.get_by_user(user_id)

    async def get_ticket_with_messages(
        self, ticket_id: UUID
    ) -> tuple[Ticket, list[TicketMessage]] | None:
        """Gets ticket with all its messages."""
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None

        messages = await self.ticket_repo.get_messages(ticket_id)
        return (ticket, messages)

    async def get_ticket_by_simple_id(self, simple_id: int) -> Ticket | None:
        """Gets ticket by simplified ID."""
        return await self.ticket_repo.get_by_simple_id(simple_id)

    async def add_user_message(
        self, ticket_id: UUID, user_id: int, message: str
    ) -> TicketMessage | None:
        """Adds user message to ticket."""
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket or ticket.user_id != user_id:
            return None

        ticket_message = TicketMessage(
            ticket_id=ticket_id,
            from_user_id=user_id,
            message=message,
            from_admin=False,
        )
        saved = await self.ticket_repo.save_message(ticket_message)

        # Update ticket status if it was responded
        if ticket.status == TicketStatus.RESPONDED:
            ticket.status = TicketStatus.OPEN
            await self.ticket_repo.update(ticket)

        return saved

    async def add_admin_response(
        self, ticket_id: UUID, admin_id: int, message: str
    ) -> TicketMessage | None:
        """Adds admin response and updates status."""
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None

        ticket_message = TicketMessage(
            ticket_id=ticket_id,
            from_user_id=admin_id,
            message=message,
            from_admin=True,
        )
        saved = await self.ticket_repo.save_message(ticket_message)

        # Update status to responded
        if ticket.status in [TicketStatus.OPEN, TicketStatus.RESPONDED]:
            ticket.status = TicketStatus.RESPONDED
            await self.ticket_repo.update(ticket)

        return saved

    async def resolve_ticket(
        self, ticket_id: UUID, admin_id: int, notes: str | None = None
    ) -> Ticket | None:
        """Marks ticket as resolved."""
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None

        ticket.update_status(TicketStatus.RESOLVED, admin_id)
        if notes:
            ticket.admin_notes = notes

        updated = await self.ticket_repo.update(ticket)
        logger.info(f"Ticket {ticket.ticket_number} resolved by admin {admin_id}")
        return updated

    async def close_ticket(
        self, ticket_id: UUID, user_id: int, is_admin: bool = False
    ) -> Ticket | None:
        """Closes ticket (by user or admin)."""
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None

        # User can only close their own tickets
        if not is_admin and ticket.user_id != user_id:
            return None

        ticket.update_status(TicketStatus.CLOSED, user_id if is_admin else None)
        updated = await self.ticket_repo.update(ticket)
        logger.info(
            f"Ticket {ticket.ticket_number} closed by {'admin' if is_admin else 'user'} {user_id}"
        )
        return updated

    async def reopen_ticket(self, ticket_id: UUID, admin_id: int) -> Ticket | None:
        """Reopens a closed ticket (admin only)."""
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None

        if ticket.status != TicketStatus.CLOSED:
            return None

        ticket.update_status(TicketStatus.OPEN)
        updated = await self.ticket_repo.update(ticket)
        logger.info(f"Ticket {ticket.ticket_number} reopened by admin {admin_id}")
        return updated

    async def get_pending_tickets(self) -> list[Ticket]:
        """Gets pending tickets for admin."""
        return await self.ticket_repo.get_all_open()

    async def get_tickets_by_category(self, category: TicketCategory) -> list[Ticket]:
        """Gets tickets by category."""
        return await self.ticket_repo.get_by_category(category)

    async def count_open_tickets(self) -> int:
        """Counts open tickets."""
        return await self.ticket_repo.count_open()
