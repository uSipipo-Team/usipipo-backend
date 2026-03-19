"""Excepciones del dominio de la aplicación."""


class DomainException(Exception):
    """Clase base para excepciones del dominio."""

    pass


class UserNotFoundError(DomainException):
    """Excepción cuando no se encuentra un usuario."""

    def __init__(self, message: str = "User not found"):
        self.message = message
        super().__init__(self.message)


class VpnKeyNotFoundError(DomainException):
    """Excepción cuando no se encuentra una clave VPN."""

    def __init__(self, message: str = "VPN key not found"):
        self.message = message
        super().__init__(self.message)


class VpnKeyLimitReachedError(DomainException):
    """Excepción cuando el usuario alcanzó el límite de claves VPN."""

    def __init__(self, message: str = "VPN key limit reached"):
        self.message = message
        super().__init__(self.message)


class InvalidVpnTypeError(DomainException):
    """Excepción cuando se proporciona un tipo de VPN inválido."""

    def __init__(self, message: str = "Invalid VPN type"):
        self.message = message
        super().__init__(self.message)


class PaymentNotFoundError(DomainException):
    """Excepción cuando no se encuentra un pago."""

    def __init__(self, message: str = "Payment not found"):
        self.message = message
        super().__init__(self.message)


class InsufficientBalanceError(DomainException):
    """Excepción cuando el usuario tiene saldo insuficiente."""

    def __init__(self, message: str = "Insufficient balance"):
        self.message = message
        super().__init__(self.message)


class PaymentExpiredError(DomainException):
    """Excepción cuando un pago ha expirado."""

    def __init__(self, message: str = "Payment expired"):
        self.message = message
        super().__init__(self.message)


class PaymentAlreadyCompletedError(DomainException):
    """Excepción cuando un pago ya está completado."""

    def __init__(self, message: str = "Payment already completed"):
        self.message = message
        super().__init__(self.message)
