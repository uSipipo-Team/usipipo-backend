"""Servicio para la gestión de paquetes de datos."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from usipipo_commons.domain.entities import DataPackage, PackageType

from src.core.application.services.user_bonus_service import UserBonusService
from src.core.domain.interfaces.i_data_package_repository import IDataPackageRepository
from src.core.domain.interfaces.i_user_repository import IUserRepository

logger = logging.getLogger(__name__)


@dataclass
class PackageOption:
    name: str
    package_type: PackageType
    data_gb: int
    stars: int
    bonus_percent: int = 0
    duration_days: int = 35


@dataclass
class SlotOption:
    name: str
    slots: int
    stars: int


PACKAGE_OPTIONS: list[PackageOption] = [
    PackageOption(
        name="Básico",
        package_type=PackageType.BASIC,
        data_gb=10,
        stars=250,
        bonus_percent=0,
    ),
    PackageOption(
        name="Estándar",
        package_type=PackageType.ESTANDAR,
        data_gb=30,
        stars=600,
        bonus_percent=10,  # +3 GB gratis -> 33 GB total
    ),
    PackageOption(
        name="Avanzado",
        package_type=PackageType.AVANZADO,
        data_gb=60,
        stars=960,
        bonus_percent=15,  # +9 GB gratis -> 69 GB total
    ),
    PackageOption(
        name="Premium",
        package_type=PackageType.PREMIUM,
        data_gb=120,
        stars=1440,
        bonus_percent=20,  # +24 GB gratis -> 144 GB total
    ),
    PackageOption(
        name="Ilimitado",
        package_type=PackageType.UNLIMITED,
        data_gb=200,
        stars=1800,
        bonus_percent=25,  # +50 GB gratis -> 250 GB total
    ),
]

SLOT_OPTIONS: list[SlotOption] = [
    SlotOption(name="+1 Clave", slots=1, stars=300),
    SlotOption(name="+3 Claves", slots=3, stars=700),
    SlotOption(name="+5 Claves", slots=5, stars=1000),
]


class DataPackageService:
    """Servicio para gestionar la lógica de negocio de los paquetes de datos."""

    def __init__(
        self,
        package_repo: IDataPackageRepository,
        user_repo: IUserRepository,
        bonus_service: UserBonusService | None = None,
    ):
        self.package_repo = package_repo
        self.user_repo = user_repo
        self.bonus_service = bonus_service or UserBonusService()

    def get_available_packages(self) -> list[PackageOption]:
        """Retorna las opciones de paquetes disponibles."""
        return PACKAGE_OPTIONS.copy()

    def get_available_slots(self) -> list[SlotOption]:
        """Retorna las opciones de slots disponibles."""
        return SLOT_OPTIONS.copy()

    def _get_package_option(self, package_type: str) -> PackageOption | None:
        try:
            pkg_type = PackageType(package_type.lower())
            for option in PACKAGE_OPTIONS:
                if option.package_type == pkg_type:
                    return option
            return None
        except ValueError:
            return None

    async def purchase_package(
        self,
        telegram_id: int,
        package_type: str,
        telegram_payment_id: str,
        current_user_id: int,
        is_referred_first_purchase: bool = False,
    ) -> tuple[DataPackage, dict[str, Any]]:
        """
        Gestiona la compra de un paquete de datos aplicando bonos.
        """
        logger.info(
            f"📦 Iniciando compra de paquete - telegram_id={telegram_id}, "
            f"package_type={package_type}, payment_id={telegram_payment_id}"
        )

        option = self._get_package_option(package_type)
        if not option:
            raise ValueError(f"Tipo de paquete inválido: {package_type}")

        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError(f"Usuario no encontrado: {telegram_id}")

        # Obtener paquetes activos para calcular bono de renovación rápida
        active_packages = await self.package_repo.get_valid_by_user(telegram_id, current_user_id)

        # Calcular bonos totales
        total_bonus_percent, bonuses = self.bonus_service.calculate_total_bonus(
            user, active_packages, is_referred_first_purchase
        )

        # Calcular datos finales con bonos
        data_limit_bytes = option.data_gb * (1024**3)
        total_multiplier = 1 + (option.bonus_percent + total_bonus_percent) / 100
        actual_data_bytes = int(data_limit_bytes * total_multiplier)

        expires_at = datetime.now(UTC) + timedelta(days=option.duration_days)

        new_package = DataPackage(
            user_id=telegram_id,
            package_type=option.package_type,
            data_limit_bytes=actual_data_bytes,
            stars_paid=option.stars,
            expires_at=expires_at,
            telegram_payment_id=telegram_payment_id,
        )

        saved_package = await self.package_repo.save(new_package, current_user_id)

        # Actualizar estadísticas del usuario
        user.purchase_count += 1
        if user.purchase_count == 1:
            user.welcome_bonus_used = True

        # Actualizar bono de lealtad
        new_loyalty = self.bonus_service.get_loyalty_bonus_for_purchase_count(user.purchase_count)
        if new_loyalty > user.loyalty_bonus_percent:
            user.loyalty_bonus_percent = new_loyalty

        await self.user_repo.update(user)

        # Desglose de bonos para la respuesta
        bonus_breakdown = {
            "base_package_bonus": option.bonus_percent,
            "user_bonuses": [b.description for b in bonuses],
            "total_bonus_percent": option.bonus_percent + total_bonus_percent,
            "base_gb": option.data_gb,
            "final_gb": actual_data_bytes / (1024**3),
        }

        logger.info(
            f"✅ Paquete comprado - user={telegram_id}, "
            f"final_gb={bonus_breakdown['final_gb']:.2f}, total_bonus={bonus_breakdown['total_bonus_percent']}%"
        )

        return saved_package, bonus_breakdown
