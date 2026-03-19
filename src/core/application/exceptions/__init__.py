"""Excepciones del dominio."""

from .domain_exceptions import (
    DomainException,
    UserNotFoundError,
    VpnKeyNotFoundError,
    VpnKeyLimitReachedError,
    InvalidVpnTypeError,
    PaymentNotFoundError,
    InsufficientBalanceError,
)

__all__ = [
    "DomainException",
    "UserNotFoundError",
    "VpnKeyNotFoundError",
    "VpnKeyLimitReachedError",
    "InvalidVpnTypeError",
    "PaymentNotFoundError",
    "InsufficientBalanceError",
]
