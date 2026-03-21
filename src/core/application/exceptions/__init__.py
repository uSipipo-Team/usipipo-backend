"""Excepciones del dominio."""

from .domain_exceptions import (
    DomainException,
    InsufficientBalanceError,
    InvalidPlanTypeError,
    InvalidVpnTypeError,
    PaymentAlreadyCompletedError,
    PaymentExpiredError,
    PaymentNotFoundError,
    SubscriptionAlreadyActiveError,
    SubscriptionNotFoundError,
    UserNotFoundError,
    VpnKeyLimitReachedError,
    VpnKeyNotFoundError,
)

__all__ = [
    "DomainException",
    "UserNotFoundError",
    "VpnKeyNotFoundError",
    "VpnKeyLimitReachedError",
    "InvalidVpnTypeError",
    "PaymentNotFoundError",
    "PaymentExpiredError",
    "PaymentAlreadyCompletedError",
    "InsufficientBalanceError",
    "InvalidPlanTypeError",
    "SubscriptionAlreadyActiveError",
    "SubscriptionNotFoundError",
]
