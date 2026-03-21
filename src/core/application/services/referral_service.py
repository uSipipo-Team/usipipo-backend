"""Servicio para la gestión del sistema de referidos."""

import logging
from typing import Any
from uuid import UUID

from usipipo_commons.domain.entities.referral import Referral

from src.core.domain.interfaces.i_referral_repository import IReferralRepository
from src.core.domain.interfaces.i_user_repository import IUserRepository
from src.shared.config import settings

logger = logging.getLogger(__name__)


class ReferralService:
    """
    Servicio para gestionar el sistema de referidos.
    Maneja el registro de nuevos referidos y la asignación de recompensas.
    """

    def __init__(
        self,
        user_repo: IUserRepository,
        referral_repo: IReferralRepository,
    ):
        self.user_repo = user_repo
        self.referral_repo = referral_repo

    async def register_referral(
        self,
        new_user_id: UUID,
        referral_code: str,
    ) -> dict[str, Any]:
        """
        Registra un nuevo referido y otorga créditos iniciales.
        """
        logger.info(f"Registrando nuevo referido: user={new_user_id}, code={referral_code}")

        try:
            # 1. Buscar al referente por código
            referrer = await self.user_repo.get_by_referral_code(referral_code)
            if not referrer:
                return {"success": False, "error": "invalid_code"}

            if referrer.id == new_user_id:
                return {"success": False, "error": "self_referral"}

            # 2. Verificar que el nuevo usuario exista y no tenga ya un referente
            new_user = await self.user_repo.get_by_id(new_user_id)
            if not new_user:
                return {"success": False, "error": "user_not_found"}

            if new_user.referred_by is not None:
                return {"success": False, "error": "already_referred"}

            # 3. Crear la relación de referido
            new_referral = Referral(referrer_id=referrer.id, referred_id=new_user_id)
            await self.referral_repo.save(new_referral)

            # 4. Otorgar créditos iniciales
            credits_referrer = settings.REFERRAL_CREDITS_PER_REFERRAL
            credits_new_user = settings.REFERRAL_BONUS_NEW_USER

            # Actualizar referente
            referrer.referral_credits += credits_referrer
            await self.user_repo.update(referrer)

            # Actualizar nuevo usuario
            new_user.referred_by = referrer.id
            new_user.referral_credits += credits_new_user
            await self.user_repo.update(new_user)

            logger.info(
                f"Referido registrado con éxito: referrer={referrer.id}, "
                f"new_user={new_user_id}, credits_referrer=+{credits_referrer}, "
                f"credits_new_user=+{credits_new_user}"
            )

            return {
                "success": True,
                "referrer_id": referrer.id,
                "credits_to_referrer": credits_referrer,
                "credits_to_new_user": credits_new_user,
            }

        except Exception as e:
            logger.error(f"Error al registrar referido: {e}")
            return {"success": False, "error": str(e)}

    async def get_referral_stats(self, user_id: UUID) -> dict[str, Any]:
        """
        Obtiene estadísticas de referidos para un usuario.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        total_referrals = await self.referral_repo.count_referrals_by_referrer(user_id)

        return {
            "referral_code": user.referral_code,
            "total_referrals": total_referrals,
            "referral_credits": user.referral_credits,
            "referred_by": user.referred_by,
        }

    async def redeem_credits_for_data(self, user_id: UUID, credits: int) -> dict[str, Any]:
        """
        Canjea créditos por datos adicionales (GB).
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "user_not_found"}

        if user.referral_credits < credits:
            return {"success": False, "error": "insufficient_credits"}

        credits_per_gb = settings.REFERRAL_CREDITS_PER_GB
        gb_to_add = credits // credits_per_gb

        if gb_to_add < 1:
            return {
                "success": False,
                "error": "insufficient_credits_for_gb",
                "required": credits_per_gb,
            }

        actual_credits = gb_to_add * credits_per_gb

        # Actualizar objeto y persistir
        user.referral_credits -= actual_credits
        user.balance_gb += float(gb_to_add)
        await self.user_repo.update(user)

        return {
            "success": True,
            "credits_spent": actual_credits,
            "gb_added": gb_to_add,
            "new_balance_gb": user.balance_gb,
        }
