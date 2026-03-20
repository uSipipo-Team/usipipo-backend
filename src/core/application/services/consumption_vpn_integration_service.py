"""ConsumptionVpnIntegrationService - Integration between consumption billing and VPN infrastructure."""

from typing import Any
from uuid import UUID

from src.core.application.services.vpn_infrastructure_service import (
    VpnInfrastructureService,
)
from src.core.domain.interfaces.i_user_repository import IUserRepository
from src.core.domain.interfaces.i_vpn_key_repository import IVpnKeyRepository


class ConsumptionVpnIntegrationService:
    """
    Servicio de integración entre modo consumo e infraestructura VPN.
    Permite bloquear/desbloquear claves de usuarios con deuda pendiente.
    """

    def __init__(
        self,
        user_repo: IUserRepository,
        key_repo: IVpnKeyRepository,
        vpn_infra_service: VpnInfrastructureService,
    ):
        """
        Inicializa el servicio de integración.

        Args:
            user_repo: Repositorio de usuarios
            key_repo: Repositorio de claves VPN
            vpn_infra_service: Servicio de infraestructura VPN
        """
        self.user_repo = user_repo
        self.key_repo = key_repo
        self.vpn_infra_service = vpn_infra_service

    async def block_user_keys(self, user_id: UUID) -> dict[str, Any]:
        """
        Bloquea todas las claves VPN de un usuario con deuda pendiente.

        Args:
            user_id: UUID del usuario

        Returns:
            Dict con {
                "success": bool,
                "keys_blocked": int,
                "keys_failed": int,
                "errors": list
            }
        """
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "keys_blocked": 0,
                    "keys_failed": 0,
                    "errors": ["Usuario no encontrado"],
                }

            keys = await self.key_repo.get_by_user_id(user_id)
            if not keys:
                # Marcar usuario como teniendo deuda aunque no tenga claves
                # (esto depende de la implementación del usuario)
                return {
                    "success": True,
                    "keys_blocked": 0,
                    "keys_failed": 0,
                    "errors": [],
                }

            keys_blocked = 0
            keys_failed = 0
            errors = []

            for key in keys:
                try:
                    result = await self.vpn_infra_service.disable_key(key.id, key.vpn_type)

                    if result.get("success"):
                        keys_blocked += 1
                    else:
                        keys_failed += 1
                        err = result.get("error", "Unknown error")
                        errors.append(f"Failed to block key {key.id}: {err}")
                except Exception as e:
                    keys_failed += 1
                    errors.append(f"Exception blocking key {key.id}: {str(e)}")

            # Marcar usuario como teniendo deuda
            # (esto requiere implementar mark_as_has_debt en User entity)
            # user.mark_as_has_debt()
            # await self.user_repo.update(user)

            return {
                "success": keys_failed == 0,
                "keys_blocked": keys_blocked,
                "keys_failed": keys_failed,
                "errors": errors,
            }

        except Exception as e:
            return {
                "success": False,
                "keys_blocked": 0,
                "keys_failed": 0,
                "errors": [f"Error al bloquear claves: {str(e)}"],
            }

    async def unblock_user_keys(self, user_id: UUID) -> dict[str, Any]:
        """
        Desbloquea todas las claves VPN de un usuario y limpia su deuda.

        Args:
            user_id: UUID del usuario

        Returns:
            Dict con {
                "success": bool,
                "keys_unblocked": int,
                "keys_failed": int,
                "errors": list
            }
        """
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "keys_unblocked": 0,
                    "keys_failed": 0,
                    "errors": ["Usuario no encontrado"],
                }

            keys = await self.key_repo.get_by_user_id(user_id)
            if not keys:
                # Limpiar deuda del usuario aunque no tenga claves
                # user.clear_debt()
                # await self.user_repo.update(user)
                return {
                    "success": True,
                    "keys_unblocked": 0,
                    "keys_failed": 0,
                    "errors": [],
                }

            keys_unblocked = 0
            keys_failed = 0
            errors = []

            for key in keys:
                try:
                    result = await self.vpn_infra_service.enable_key(key.id, key.vpn_type)

                    if result.get("success"):
                        keys_unblocked += 1
                    else:
                        keys_failed += 1
                        err = result.get("error", "Unknown error")
                        errors.append(f"Failed to unblock key {key.id}: {err}")
                except Exception as e:
                    keys_failed += 1
                    errors.append(f"Exception unblocking key {key.id}: {str(e)}")

            # Limpiar deuda del usuario
            # user.clear_debt()
            # await self.user_repo.update(user)

            return {
                "success": keys_failed == 0,
                "keys_unblocked": keys_unblocked,
                "keys_failed": keys_failed,
                "errors": errors,
            }

        except Exception as e:
            return {
                "success": False,
                "keys_unblocked": 0,
                "keys_failed": 0,
                "errors": [f"Error al desbloquear claves: {str(e)}"],
            }

    async def check_can_create_key(self, user_id: UUID) -> dict[str, Any]:
        """
        Verifica si un usuario puede crear una nueva clave VPN.

        Args:
            user_id: UUID del usuario

        Returns:
            Dict con {
                "can_create": bool,
                "reason": str
            }
        """
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return {"can_create": False, "reason": "Usuario no encontrado"}

            # Verificar si el usuario tiene deuda pendiente
            # if user.has_debt:
            #     return {"can_create": False, "reason": "Usuario tiene deuda pendiente"}

            # Verificar límite de claves
            from usipipo_commons.constants.plans import MAX_KEYS_PER_USER

            keys = await self.key_repo.get_by_user_id(user_id)
            active_keys = [k for k in keys if k.status.value == "active"]

            if len(active_keys) >= MAX_KEYS_PER_USER:
                return {
                    "can_create": False,
                    "reason": f"Límite de claves alcanzado ({MAX_KEYS_PER_USER})",
                }

            return {"can_create": True, "reason": ""}

        except Exception as e:
            return {"can_create": False, "reason": f"Error: {str(e)}"}
