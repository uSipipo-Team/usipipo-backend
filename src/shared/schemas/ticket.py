"""Schemas for tickets."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from usipipo_commons.domain.entities import TicketCategory, TicketPriority, TicketStatus


class TicketResponse(BaseModel):
    """Response schema for ticket."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticket_number: str
    user_id: int
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    subject: str
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
    resolved_by: int | None = None
    admin_notes: str | None = None


class TicketWithMessagesResponse(TicketResponse):
    """Response schema for ticket with messages."""

    messages: list["TicketMessageResponse"]


class TicketMessageResponse(BaseModel):
    """Response schema for ticket message."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticket_id: UUID
    from_user_id: int
    message: str
    from_admin: bool
    created_at: datetime


class TicketCreateRequest(BaseModel):
    """Request schema for creating a ticket."""

    category: TicketCategory = Field(..., description="Ticket category")
    subject: str = Field(..., min_length=5, max_length=200, description="Ticket subject")
    message: str = Field(..., min_length=10, description="Initial message")


class TicketUpdateRequest(BaseModel):
    """Request schema for updating a ticket."""

    status: TicketStatus | None = Field(None, description="New ticket status")
    admin_notes: str | None = Field(None, description="Admin notes")


class TicketMessageRequest(BaseModel):
    """Request schema for adding a message to a ticket."""

    message: str = Field(..., min_length=1, description="Message content")


class TicketResolveRequest(BaseModel):
    """Request schema for resolving a ticket."""

    notes: str | None = Field(None, description="Resolution notes")


class TicketStatsResponse(BaseModel):
    """Response schema for ticket statistics."""

    open_count: int = Field(..., description="Number of open tickets")
    responded_count: int = Field(..., description="Number of responded tickets")
    resolved_count: int = Field(..., description="Number of resolved tickets")
    closed_count: int = Field(..., description="Number of closed tickets")
