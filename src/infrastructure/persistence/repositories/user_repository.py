"""Repositorio de usuarios con SQLAlchemy."""

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.user import User

from src.core.domain.interfaces.i_user_repository import IUserRepository
from src.infrastructure.persistence.models.user_model import UserModel


class UserRepository(IUserRepository):
    """Implementación de repositorio de usuarios con SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[User]:
        """
        Obtiene todos los usuarios.

        Returns:
            Lista de todos los usuarios
        """
        result = await self.session.execute(select(UserModel))
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Obtiene usuario por ID.

        Args:
            user_id: UUID del usuario

        Returns:
            User o None si no existe
        """
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
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

    async def get_by_referral_code(self, referral_code: str) -> User | None:
        """
        Obtiene usuario por código de referido.

        Args:
            referral_code: Código de referido

        Returns:
            User o None si no existe
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.referral_code == referral_code)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def update_referral_credits(self, user_id: UUID, credits: int) -> bool:
        """
        Actualiza los créditos de referido de un usuario.

        Args:
            user_id: UUID del usuario
            credits: Créditos a añadir (pueden ser negativos)

        Returns:
            True si se actualizó correctamente
        """
        try:
            query = (
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(referral_credits=UserModel.referral_credits + credits)
            )
            await self.session.execute(query)
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            return False

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
        model = await self.session.merge(model)
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
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False
