"""Interface for ticket repository."""

from uuid import UUID

from usipipo_commons.domain.entities import Ticket, TicketCategory, TicketMessage, TicketStatus


class ITicketRepository:
    """Contract for ticket repository."""

    async def save(self, ticket: Ticket) -> Ticket:
        """Saves a new ticket."""
        ...

    async def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        """Gets a ticket by its ID."""
        ...

    async def get_by_simple_id(self, simple_id: int) -> Ticket | None:
        """Gets a ticket by its simplified ID (int)."""
        ...

    async def get_by_user(self, user_id: int) -> list[Ticket]:
        """Gets all tickets from a user."""
        ...

    async def update(self, ticket: Ticket) -> Ticket:
        """Updates an existing ticket."""
        ...

    async def get_by_status(self, status: TicketStatus) -> list[Ticket]:
        """Gets tickets by status."""
        ...

    async def get_by_category(self, category: TicketCategory) -> list[Ticket]:
        """Gets tickets by category."""
        ...

    async def get_all_open(self) -> list[Ticket]:
        """Gets all open tickets (OPEN or RESPONDED)."""
        ...

    async def save_message(self, message: TicketMessage) -> TicketMessage:
        """Saves a ticket message."""
        ...

    async def get_messages(self, ticket_id: UUID) -> list[TicketMessage]:
        """Gets all messages from a ticket."""
        ...

    async def count_open(self) -> int:
        """Counts open tickets."""
        ...
