"""Excepciones del dominio."""

from .domain_exceptions import (
    DomainException,
    InsufficientBalanceError,
    InvalidVpnTypeError,
    PaymentAlreadyCompletedError,
    PaymentExpiredError,
    PaymentNotFoundError,
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
]
