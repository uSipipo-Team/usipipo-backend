"""Interfaces de repositorio."""

from .i_consumption_billing_repository import IConsumptionBillingRepository
from .i_subscription_repository import ISubscriptionRepository
from .i_subscription_transaction_repository import ISubscriptionTransactionRepository
from .i_user_repository import IUserRepository
from .i_vpn_repository import IVPNRepository

__all__ = [
    "IUserRepository",
    "IVPNRepository",
    "ISubscriptionRepository",
    "ISubscriptionTransactionRepository",
    "IConsumptionBillingRepository",
]
