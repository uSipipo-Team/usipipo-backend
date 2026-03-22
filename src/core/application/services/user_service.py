"""Servicios de aplicación para gestión de usuarios."""

import uuid
from datetime import datetime

from usipipo_commons.constants.plans import FREE_GB
from usipipo_commons.domain.entities.user import User

from src.core.application.exceptions import UserNotFoundError
from src.core.domain.interfaces.i_user_repository import IUserRepository


class UserService:
    """Servicio de aplicación para gestión de usuarios."""

    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Obtiene usuario por ID."""
        return await self.user_repo.get_by_id(user_id)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Obtiene usuario por Telegram ID."""
        return await self.user_repo.get_by_telegram_id(telegram_id)

    async def get_or_create_by_telegram(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        referral_code: str | None = None,
    ) -> User:
        """
        Obtiene usuario por Telegram ID o crea uno nuevo si no existe.

        Args:
            telegram_id: El ID de Telegram del usuario
            username: Username de Telegram
            first_name: Nombre del usuario
            last_name: Apellido del usuario
            referral_code: Código de referido opcional

        Returns:
            El usuario existente o el nuevo usuario creado
        """
        # Intentar obtener usuario existente
        existing_user = await self.get_by_telegram_id(telegram_id)
        if existing_user:
            # Actualizar información si cambió
            await self.user_repo.update(
                User(
                    id=existing_user.id,
                    telegram_id=telegram_id,
                    username=username or existing_user.username,
                    first_name=first_name or existing_user.first_name,
                    last_name=last_name or existing_user.last_name,
                    is_admin=existing_user.is_admin,
                    created_at=existing_user.created_at,
                    updated_at=datetime.utcnow(),
                    balance_gb=existing_user.balance_gb,
                    total_purchased_gb=existing_user.total_purchased_gb,
                    referral_code=existing_user.referral_code,
                    referred_by=existing_user.referred_by,
                )
            )
            return existing_user

        # Generar código de referido único si no se proporciona
        # Formato: ref_ + 16 chars hex (max 20 chars para caber en DB)
        if not referral_code:
            referral_code = f"ref_{uuid.uuid4().hex[:16]}"

        # Crear nuevo usuario
        new_user = User(
            id=uuid.uuid4(),
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_admin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            balance_gb=FREE_GB,  # 5 GB gratis por defecto
            total_purchased_gb=0.0,
            referral_code=referral_code,
            referred_by=None,
        )

        return await self.user_repo.create(new_user)

    async def create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        referral_code: str | None = None,
        referred_by: uuid.UUID | None = None,
    ) -> User:
        """
        Crea un nuevo usuario.

        Args:
            telegram_id: El ID de Telegram del usuario
            username: Username de Telegram
            first_name: Nombre del usuario
            last_name: Apellido del usuario
            referral_code: Código de referido opcional
            referred_by: UUID del usuario que refirió (opcional)

        Returns:
            El usuario creado
        """
        # Verificar que no exista
        existing = await self.get_by_telegram_id(telegram_id)
        if existing:
            raise ValueError(f"User with telegram_id {telegram_id} already exists")

        # Generar código de referido único si no se proporciona
        # Formato: ref_ + 16 chars hex (max 20 chars para caber en DB)
        if not referral_code:
            referral_code = f"ref_{uuid.uuid4().hex[:16]}"

        new_user = User(
            id=uuid.uuid4(),
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_admin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            balance_gb=FREE_GB,
            total_purchased_gb=0.0,
            referral_code=referral_code,
            referred_by=referred_by,
        )

        return await self.user_repo.create(new_user)

    async def update_user(
        self,
        user_id: uuid.UUID,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        balance_gb: float | None = None,
    ) -> User:
        """
        Actualiza información del usuario.

        Args:
            user_id: UUID del usuario
            username: Nuevo username
            first_name: Nuevo nombre
            last_name: Nuevo apellido
            balance_gb: Nuevo saldo en GB

        Returns:
            El usuario actualizado

        Raises:
            UserNotFoundError: Si el usuario no existe
        """
        existing_user = await self.get_by_id(user_id)
        if not existing_user:
            raise UserNotFoundError(f"User {user_id} not found")

        updated_user = User(
            id=existing_user.id,
            telegram_id=existing_user.telegram_id,
            username=username if username is not None else existing_user.username,
            first_name=first_name if first_name is not None else existing_user.first_name,
            last_name=last_name if last_name is not None else existing_user.last_name,
            is_admin=existing_user.is_admin,
            created_at=existing_user.created_at,
            updated_at=datetime.utcnow(),
            balance_gb=balance_gb if balance_gb is not None else existing_user.balance_gb,
            total_purchased_gb=existing_user.total_purchased_gb,
            referral_code=existing_user.referral_code,
            referred_by=existing_user.referred_by,
        )

        return await self.user_repo.update(updated_user)

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """
        Elimina un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            True si se eliminó, False si no existía
        """
        return await self.user_repo.delete(user_id)

    async def add_balance(self, user_id: uuid.UUID, amount_gb: float) -> User:
        """
        Agrega saldo en GB a un usuario.

        Args:
            user_id: UUID del usuario
            amount_gb: Cantidad de GB a agregar

        Returns:
            El usuario actualizado

        Raises:
            UserNotFoundError: Si el usuario no existe
        """
        existing_user = await self.get_by_id(user_id)
        if not existing_user:
            raise UserNotFoundError(f"User {user_id} not found")

        updated_user = User(
            id=existing_user.id,
            telegram_id=existing_user.telegram_id,
            username=existing_user.username,
            first_name=existing_user.first_name,
            last_name=existing_user.last_name,
            is_admin=existing_user.is_admin,
            created_at=existing_user.created_at,
            updated_at=datetime.utcnow(),
            balance_gb=existing_user.balance_gb + amount_gb,
            total_purchased_gb=existing_user.total_purchased_gb + amount_gb,
            referral_code=existing_user.referral_code,
            referred_by=existing_user.referred_by,
        )

        return await self.user_repo.update(updated_user)

    async def apply_referral_bonus(
        self,
        referrer_user_id: uuid.UUID,
        referred_user_id: uuid.UUID,
    ) -> None:
        """
        Aplica bono de referido al usuario que refirió.

        Args:
            referrer_user_id: UUID del usuario que refirió
            referred_user_id: UUID del usuario que fue referido
        """
        # El bono se aplica cuando el referido realiza una compra
        # Esto se maneja en el servicio de pagos
        pass
