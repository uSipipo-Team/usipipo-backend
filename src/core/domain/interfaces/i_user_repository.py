"""Interfaces de repositorio para la capa de dominio."""

from abc import ABC, abstractmethod
from uuid import UUID

from usipipo_commons.domain.entities.user import User


class IUserRepository(ABC):
    """Contrato para repositorio de usuarios."""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Obtiene usuario por ID."""
        pass

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Obtiene usuario por Telegram ID."""
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
