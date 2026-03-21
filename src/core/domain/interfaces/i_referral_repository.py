"""Interfaces para la persistencia de referidos."""

import uuid
from typing import Protocol

from usipipo_commons.domain.entities.referral import Referral


class IReferralRepository(Protocol):
    """Contrato para el repositorio de referidos."""

    async def save(self, referral: Referral) -> Referral:
        """Guarda o actualiza una relación de referido."""
        ...

    async def get_by_id(self, referral_id: uuid.UUID) -> Referral | None:
        """Obtiene un referido por su ID."""
        ...

    async def get_by_referred_id(self, referred_id: uuid.UUID) -> Referral | None:
        """Busca quién refirió a un usuario específico."""
        ...

    async def get_referrals_by_referrer(self, referrer_id: uuid.UUID) -> list[Referral]:
        """Obtiene la lista de usuarios referidos por alguien."""
        ...

    async def count_referrals_by_referrer(self, referrer_id: uuid.UUID) -> int:
        """Cuenta el total de referidos de un usuario."""
        ...

    async def mark_bonus_applied(self, referral_id: uuid.UUID) -> bool:
        """Marca un bono de referido como ya aplicado."""
        ...
