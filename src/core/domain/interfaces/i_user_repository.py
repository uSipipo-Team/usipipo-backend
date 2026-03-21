"""Interfaces de repositorio para la capa de dominio."""

from abc import ABC, abstractmethod
from uuid import UUID

from usipipo_commons.domain.entities.user import User


class IUserRepository(ABC):
    """Contrato para repositorio de usuarios."""

    @abstractmethod
    async def get_all(self) -> list[User]:
        """Obtiene todos los usuarios."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Obtiene usuario por ID."""
        pass

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Obtiene usuario por Telegram ID."""
        pass

    @abstractmethod
    async def get_by_referral_code(self, referral_code: str) -> User | None:
        """Obtiene usuario por código de referido."""
        pass

    @abstractmethod
    async def update_referral_credits(self, user_id: UUID, credits: int) -> bool:
        """Actualiza los créditos de referido de un usuario."""
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        """Crea un nuevo usuario."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Actualiza usuario existente."""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Elimina usuario."""
        pass
