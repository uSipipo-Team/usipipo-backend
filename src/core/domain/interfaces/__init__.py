"""Interfaces de repositorio."""

from .i_admin_service import (
    IAdminKeyService,
    IAdminServerService,
    IAdminStatsService,
    IAdminUserService,
)
from .i_consumption_billing_repository import IConsumptionBillingRepository
from .i_subscription_repository import ISubscriptionRepository
from .i_subscription_transaction_repository import ISubscriptionTransactionRepository
from .i_ticket_repository import ITicketRepository
from .i_user_repository import IUserRepository
from .i_vpn_repository import IVPNRepository

__all__ = [
    "IUserRepository",
    "IVPNRepository",
    "ISubscriptionRepository",
    "ISubscriptionTransactionRepository",
    "IConsumptionBillingRepository",
    "ITicketRepository",
    "IAdminStatsService",
    "IAdminUserService",
    "IAdminKeyService",
    "IAdminServerService",
]
