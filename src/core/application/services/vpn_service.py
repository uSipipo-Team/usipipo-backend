"""Servicios de aplicación para gestión de VPN."""

import uuid
from datetime import datetime, timedelta

from usipipo_commons.constants.plans import MAX_KEYS_PER_USER
from usipipo_commons.domain.entities.vpn_key import VpnKey
from usipipo_commons.domain.enums.key_status import KeyStatus
from usipipo_commons.domain.enums.vpn_type import VpnType

from src.core.application.exceptions import (
    InvalidVpnTypeError,
    UserNotFoundError,
    VpnKeyLimitReachedError,
    VpnKeyNotFoundError,
)
from src.core.domain.interfaces.i_user_repository import IUserRepository
from src.core.domain.interfaces.i_vpn_repository import IVPNRepository


class VpnService:
    """Servicio de aplicación para gestión de claves VPN."""

    def __init__(
        self,
        user_repo: IUserRepository,
        vpn_repo: IVPNRepository,
    ):
        self.user_repo = user_repo
        self.vpn_repo = vpn_repo

    async def create_key(
        self,
        user_id: uuid.UUID,
        name: str,
        vpn_type: str,
        data_limit_gb: float = 5.0,
    ) -> VpnKey:
        """
        Crea una nueva clave VPN.

        Args:
            user_id: UUID del usuario propietario
            name: Nombre descriptivo de la clave
            vpn_type: Tipo de VPN ("wireguard" o "outline")
            data_limit_gb: Límite de datos en GB

        Returns:
            La clave VPN creada

        Raises:
            UserNotFoundError: Si el usuario no existe
            VpnKeyLimitReachedError: Si el usuario alcanzó el límite de claves
            InvalidVpnTypeError: Si el tipo de VPN es inválido
        """
        # Verificar usuario
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        # Validar tipo de VPN
        try:
            vpn_type_enum = VpnType(vpn_type.lower())
        except ValueError:
            raise InvalidVpnTypeError(f"Invalid VPN type: {vpn_type}")

        # Verificar límite de claves
        existing_keys = await self.vpn_repo.get_by_user_id(user_id)
        active_keys = [k for k in existing_keys if k.status == KeyStatus.ACTIVE]

        if len(active_keys) >= MAX_KEYS_PER_USER:
            raise VpnKeyLimitReachedError(f"User reached max keys ({MAX_KEYS_PER_USER})")

        # Generar config según tipo de VPN
        # NOTA: Esto se implementará cuando se conecte con los proveedores VPN
        config = self._generate_placeholder_config(vpn_type_enum, name)

        # Calcular fecha de expiración (30 días por defecto)
        expires_at = datetime.utcnow() + timedelta(days=30)

        # Crear entidad
        vpn_key = VpnKey(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name,
            vpn_type=vpn_type_enum,
            status=KeyStatus.ACTIVE,
            config=config,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_used_at=None,
            data_used_gb=0.0,
            data_limit_gb=data_limit_gb,
        )

        # Persistir
        return await self.vpn_repo.create(vpn_key)

    async def get_key_by_id(self, key_id: uuid.UUID) -> VpnKey | None:
        """
        Obtiene una clave VPN por ID.

        Args:
            key_id: UUID de la clave

        Returns:
            La clave VPN o None si no existe
        """
        return await self.vpn_repo.get_by_id(key_id)

    async def get_user_keys(self, user_id: uuid.UUID) -> list[VpnKey]:
        """
        Obtiene todas las claves VPN de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Lista de claves VPN del usuario
        """
        return await self.vpn_repo.get_by_user_id(user_id)

    async def delete_key(self, user_id: uuid.UUID, key_id: uuid.UUID) -> bool:
        """
        Elimina una clave VPN.

        Args:
            user_id: UUID del usuario propietario
            key_id: UUID de la clave a eliminar

        Returns:
            True si se eliminó, False si no existía

        Raises:
            VpnKeyNotFoundError: Si la clave no existe
            PermissionError: Si el usuario no es propietario de la clave
        """
        key = await self.vpn_repo.get_by_id(key_id)
        if not key:
            raise VpnKeyNotFoundError(f"Key {key_id} not found")

        # Verificar propiedad
        if key.user_id != user_id:
            raise PermissionError("User does not own this key")

        # Revocar en proveedor VPN (placeholder por ahora)
        await self._revoke_from_provider(key)

        # Eliminar de BD
        return await self.vpn_repo.delete(key_id)

    async def update_key(
        self,
        user_id: uuid.UUID,
        key_id: uuid.UUID,
        name: str | None = None,
        data_limit_gb: float | None = None,
    ) -> VpnKey:
        """
        Actualiza una clave VPN.

        Args:
            user_id: UUID del usuario propietario
            key_id: UUID de la clave
            name: Nuevo nombre (opcional)
            data_limit_gb: Nuevo límite de datos (opcional)

        Returns:
            La clave VPN actualizada

        Raises:
            VpnKeyNotFoundError: Si la clave no existe
            PermissionError: Si el usuario no es propietario de la clave
        """
        key = await self.vpn_repo.get_by_id(key_id)
        if not key:
            raise VpnKeyNotFoundError(f"Key {key_id} not found")

        # Verificar propiedad
        if key.user_id != user_id:
            raise PermissionError("User does not own this key")

        # Actualizar campos
        updated_key = VpnKey(
            id=key.id,
            user_id=key.user_id,
            name=name if name is not None else key.name,
            vpn_type=key.vpn_type,
            status=key.status,
            config=key.config,
            created_at=key.created_at,
            expires_at=key.expires_at,
            last_used_at=key.last_used_at,
            data_used_gb=key.data_used_gb,
            data_limit_gb=data_limit_gb if data_limit_gb is not None else key.data_limit_gb,
        )

        return await self.vpn_repo.update(updated_key)

    async def revoke_key(self, user_id: uuid.UUID, key_id: uuid.UUID) -> VpnKey:
        """
        Revoca una clave VPN (la marca como revocada).

        Args:
            user_id: UUID del usuario propietario
            key_id: UUID de la clave

        Returns:
            La clave VPN actualizada

        Raises:
            VpnKeyNotFoundError: Si la clave no existe
            PermissionError: Si el usuario no es propietario de la clave
        """
        key = await self.vpn_repo.get_by_id(key_id)
        if not key:
            raise VpnKeyNotFoundError(f"Key {key_id} not found")

        # Verificar propiedad
        if key.user_id != user_id:
            raise PermissionError("User does not own this key")

        # Revocar en proveedor VPN
        await self._revoke_from_provider(key)

        # Actualizar estado
        updated_key = VpnKey(
            id=key.id,
            user_id=key.user_id,
            name=key.name,
            vpn_type=key.vpn_type,
            status=KeyStatus.REVOKED,
            config=key.config,
            created_at=key.created_at,
            expires_at=key.expires_at,
            last_used_at=key.last_used_at,
            data_used_gb=key.data_used_gb,
            data_limit_gb=key.data_limit_gb,
        )

        return await self.vpn_repo.update(updated_key)

    def _generate_placeholder_config(self, vpn_type: VpnType, name: str) -> str:
        """
        Genera una configuración placeholder para la VPN.

        NOTA: Esto se reemplazará cuando se implementen los clientes VPN reales.

        Args:
            vpn_type: Tipo de VPN
            name: Nombre de la clave

        Returns:
            Configuración de VPN (string)
        """
        if vpn_type == VpnType.WIREGUARD:
            return f"[WireGuard Placeholder Config for {name}]"
        elif vpn_type == VpnType.OUTLINE:
            return f"ss://outline-placeholder-config-for-{name}"
        return ""

    async def _revoke_from_provider(self, key: VpnKey) -> None:
        """
        Revoca la clave del proveedor VPN.

        NOTA: Esto se implementará cuando se conecte con los proveedores VPN reales.

        Args:
            key: La clave VPN a revocar
        """
        # Placeholder para la revocación real
        # WireGuard: await self.wireguard_client.revoke_key(key.config)
        # Outline: await self.outline_client.revoke_key(key.id)
        pass

    async def get_active_keys_count(self, user_id: uuid.UUID) -> int:
        """
        Obtiene la cantidad de claves activas de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Cantidad de claves activas
        """
        keys = await self.vpn_repo.get_by_user_id(user_id)
        return len([k for k in keys if k.status == KeyStatus.ACTIVE])

    async def can_create_more_keys(self, user_id: uuid.UUID) -> bool:
        """
        Verifica si el usuario puede crear más claves.

        Args:
            user_id: UUID del usuario

        Returns:
            True si puede crear más claves, False si alcanzó el límite
        """
        active_count = await self.get_active_keys_count(user_id)
        return active_count < MAX_KEYS_PER_USER
