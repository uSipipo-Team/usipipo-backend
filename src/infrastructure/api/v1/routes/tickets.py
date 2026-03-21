"""Routes for ticket management."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from usipipo_commons.domain.entities import TicketStatus
from usipipo_commons.domain.entities.user import User

from src.core.application.services.ticket_service import TicketService
from src.infrastructure.api.v1.deps import get_current_user, get_ticket_service
from src.shared.schemas.ticket import (
    TicketCreateRequest,
    TicketMessageRequest,
    TicketMessageResponse,
    TicketResolveRequest,
    TicketResponse,
    TicketStatsResponse,
    TicketWithMessagesResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket(
    request: TicketCreateRequest,
    current_user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Creates a new support ticket.

    Requires authentication. User's category determines automatic priority.

    Args:
        request: Ticket creation request with category, subject, and message
        current_user: Authenticated user
        ticket_service: Ticket service

    Returns:
        TicketResponse: Created ticket

    Raises:
        HTTPException: 400 if ticket creation fails
    """
    try:
        ticket = await ticket_service.create_ticket(
            user_id=current_user.telegram_id,
            category=request.category,
            subject=request.subject,
            message=request.message,
        )

        return TicketResponse(
            id=ticket.id,
            ticket_number=ticket.ticket_number,
            user_id=ticket.user_id,
            category=ticket.category,
            priority=ticket.priority,
            status=ticket.status,
            subject=ticket.subject,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            resolved_at=ticket.resolved_at,
            resolved_by=ticket.resolved_by,
            admin_notes=ticket.admin_notes,
        )
    except Exception as e:
        logger.error(f"Failed to create ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create ticket: {str(e)}"
        )


@router.get(
    "",
    response_model=list[TicketResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_tickets(
    current_user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Gets all tickets for the authenticated user.

    Requires authentication.

    Args:
        current_user: Authenticated user
        ticket_service: Ticket service

    Returns:
        list[TicketResponse]: List of user's tickets
    """
    tickets = await ticket_service.get_user_tickets(current_user.telegram_id)
    return [
        TicketResponse(
            id=t.id,
            ticket_number=t.ticket_number,
            user_id=t.user_id,
            category=t.category,
            priority=t.priority,
            status=t.status,
            subject=t.subject,
            created_at=t.created_at,
            updated_at=t.updated_at,
            resolved_at=t.resolved_at,
            resolved_by=t.resolved_by,
            admin_notes=t.admin_notes,
        )
        for t in tickets
    ]


@router.get(
    "/{ticket_id}",
    response_model=TicketWithMessagesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Gets a specific ticket with all its messages.

    Requires authentication. Users can only view their own tickets.

    Args:
        ticket_id: Ticket UUID
        current_user: Authenticated user
        ticket_service: Ticket service

    Returns:
        TicketWithMessagesResponse: Ticket with messages

    Raises:
        HTTPException: 404 if ticket not found, 403 if user doesn't own ticket
    """
    from uuid import UUID

    try:
        ticket_uuid = UUID(ticket_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ticket ID format"
        )

    result = await ticket_service.get_ticket_with_messages(ticket_uuid)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    ticket, messages = result

    # Check ownership (non-admin users can only view their own tickets)
    if not current_user.is_admin and ticket.user_id != current_user.telegram_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own tickets"
        )

    return TicketWithMessagesResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        user_id=ticket.user_id,
        category=ticket.category,
        priority=ticket.priority,
        status=ticket.status,
        subject=ticket.subject,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
        resolved_by=ticket.resolved_by,
        admin_notes=ticket.admin_notes,
        messages=[
            TicketMessageResponse(
                id=m.id,
                ticket_id=m.ticket_id,
                from_user_id=m.from_user_id,
                message=m.message,
                from_admin=m.from_admin,
                created_at=m.created_at,
            )
            for m in messages
        ],
    )


@router.post(
    "/{ticket_id}/messages",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def add_message(
    ticket_id: str,
    request: TicketMessageRequest,
    current_user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Adds a message to a ticket.

    Requires authentication. Users can only message their own tickets.

    Args:
        ticket_id: Ticket UUID
        request: Message content
        current_user: Authenticated user
        ticket_service: Ticket service

    Returns:
        dict: Success message

    Raises:
        HTTPException: 404 if ticket not found, 403 if user doesn't own ticket
    """
    from uuid import UUID

    try:
        ticket_uuid = UUID(ticket_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ticket ID format"
        )

    ticket = (
        await ticket_service.get_ticket_by_simple_id(int(ticket_id[:8], 16))
        if ticket_id[:8].isdigit()
        else None
    )
    if not ticket:
        ticket_result = await ticket_service.get_ticket_with_messages(ticket_uuid)
        ticket = ticket_result[0] if ticket_result else None

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Check ownership
    if not current_user.is_admin and ticket.user_id != current_user.telegram_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only message your own tickets"
        )

    if current_user.is_admin:
        await ticket_service.add_admin_response(
            ticket_uuid, current_user.telegram_id, request.message
        )
    else:
        await ticket_service.add_user_message(
            ticket_uuid, current_user.telegram_id, request.message
        )

    return {"message": "Message added successfully"}


@router.post(
    "/{ticket_id}/resolve",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
)
async def resolve_ticket(
    ticket_id: str,
    request: TicketResolveRequest,
    current_user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Resolves a ticket (admin only).

    Requires admin authentication.

    Args:
        ticket_id: Ticket UUID
        request: Resolution notes
        current_user: Authenticated admin user
        ticket_service: Ticket service

    Returns:
        TicketResponse: Resolved ticket

    Raises:
        HTTPException: 403 if not admin, 404 if ticket not found
    """
    from uuid import UUID

    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    try:
        ticket_uuid = UUID(ticket_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ticket ID format"
        )

    ticket = await ticket_service.resolve_ticket(
        ticket_uuid, current_user.telegram_id, request.notes
    )
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    return TicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        user_id=ticket.user_id,
        category=ticket.category,
        priority=ticket.priority,
        status=ticket.status,
        subject=ticket.subject,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
        resolved_by=ticket.resolved_by,
        admin_notes=ticket.admin_notes,
    )


@router.post(
    "/{ticket_id}/close",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
)
async def close_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Closes a ticket.

    Users can close their own tickets. Admins can close any ticket.

    Args:
        ticket_id: Ticket UUID
        current_user: Authenticated user
        ticket_service: Ticket service

    Returns:
        TicketResponse: Closed ticket

    Raises:
        HTTPException: 403 if user doesn't own ticket, 404 if not found
    """
    from uuid import UUID

    try:
        ticket_uuid = UUID(ticket_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ticket ID format"
        )

    ticket = await ticket_service.close_ticket(
        ticket_uuid, current_user.telegram_id, is_admin=current_user.is_admin
    )
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if not current_user.is_admin and ticket.user_id != current_user.telegram_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only close your own tickets"
        )

    return TicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        user_id=ticket.user_id,
        category=ticket.category,
        priority=ticket.priority,
        status=ticket.status,
        subject=ticket.subject,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
        resolved_by=ticket.resolved_by,
        admin_notes=ticket.admin_notes,
    )


@router.get(
    "/admin/pending",
    response_model=list[TicketResponse],
    status_code=status.HTTP_200_OK,
)
async def get_pending_tickets(
    current_user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Gets all pending tickets (admin only).

    Requires admin authentication. Returns open and responded tickets.

    Args:
        current_user: Authenticated admin user
        ticket_service: Ticket service

    Returns:
        list[TicketResponse]: List of pending tickets

    Raises:
        HTTPException: 403 if not admin
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    tickets = await ticket_service.get_pending_tickets()
    return [
        TicketResponse(
            id=t.id,
            ticket_number=t.ticket_number,
            user_id=t.user_id,
            category=t.category,
            priority=t.priority,
            status=t.status,
            subject=t.subject,
            created_at=t.created_at,
            updated_at=t.updated_at,
            resolved_at=t.resolved_at,
            resolved_by=t.resolved_by,
            admin_notes=t.admin_notes,
        )
        for t in tickets
    ]


@router.get(
    "/admin/stats",
    response_model=TicketStatsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_ticket_stats(
    current_user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """
    Gets ticket statistics (admin only).

    Requires admin authentication.

    Args:
        current_user: Authenticated admin user
        ticket_service: Ticket service

    Returns:
        TicketStatsResponse: Ticket statistics

    Raises:
        HTTPException: 403 if not admin
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    open_count = await ticket_service.count_open_tickets()

    # Get all tickets and count by status
    all_tickets = await ticket_service.get_pending_tickets()
    responded_count = sum(1 for t in all_tickets if t.status == TicketStatus.RESPONDED)
    open_status_count = open_count - responded_count

    return TicketStatsResponse(
        open_count=open_status_count,
        responded_count=responded_count,
        resolved_count=0,  # Would need additional query
        closed_count=0,  # Would need additional query
    )
