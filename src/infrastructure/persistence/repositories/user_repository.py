"""Repositorio de usuarios con SQLAlchemy."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from usipipo_commons.domain.entities.user import User
from src.core.domain.interfaces.i_user_repository import IUserRepository
from src.infrastructure.persistence.models.user_model import UserModel


class UserRepository(IUserRepository):
    """Implementación de repositorio de usuarios con SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Obtiene usuario por ID.

        Args:
            user_id: UUID del usuario

        Returns:
            User o None si no existe
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Obtiene usuario por Telegram ID.

        Args:
            telegram_id: ID de Telegram

        Returns:
            User o None si no existe
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def create(self, user: User) -> User:
        """
        Crea un nuevo usuario.

        Args:
            user: Usuario a crear

        Returns:
            Usuario creado
        """
        model = UserModel.from_entity(user)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_entity()

    async def update(self, user: User) -> User:
        """
        Actualiza usuario existente.

        Args:
            user: Usuario con datos actualizados

        Returns:
            Usuario actualizado
        """
        model = UserModel.from_entity(user)
        await self.session.merge(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_entity()

    async def delete(self, user_id: UUID) -> bool:
        """
        Elimina usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            True si se eliminó, False si no existía
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False
