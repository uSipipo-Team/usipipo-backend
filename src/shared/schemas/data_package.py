"""Esquemas Pydantic para paquetes de datos."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from usipipo_commons.domain.entities.data_package import PackageType


class PackageOptionResponse(BaseModel):
    """Opción de paquete disponible."""

    name: str
    package_type: PackageType
    data_gb: int
    stars: int
    bonus_percent: int
    duration_days: int


class SlotOptionResponse(BaseModel):
    """Opción de slots de claves disponible."""

    name: str
    slots: int
    stars: int


class DataPackageResponse(BaseModel):
    """Respuesta con información de un paquete de datos."""

    id: UUID
    user_id: int
    package_type: PackageType
    data_limit_bytes: int
    data_used_bytes: int
    remaining_bytes: int
    stars_paid: int
    purchased_at: datetime
    expires_at: datetime
    is_active: bool
    is_expired: bool
    is_valid: bool
    telegram_payment_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DataPackagePurchaseRequest(BaseModel):
    """Solicitud de compra de un paquete de datos."""

    package_type: str = Field(..., description="Tipo de paquete (basic, estandar, etc.)")
    telegram_payment_id: str = Field(..., description="ID de pago de Telegram")
    is_referred_first_purchase: bool = Field(
        False, description="Si es la primera compra de un referido"
    )


class BonusBreakdownResponse(BaseModel):
    """Desglose de bonos aplicados a una compra."""

    base_package_bonus: int
    user_bonuses: list[str]
    total_bonus_percent: int
    base_gb: int
    final_gb: float


class PurchaseResponse(BaseModel):
    """Respuesta tras la compra de un paquete."""

    package: DataPackageResponse
    bonuses: BonusBreakdownResponse


class UserPackagesResponse(BaseModel):
    """Respuesta con la lista de paquetes de un usuario."""

    packages: list[DataPackageResponse]
    total_count: int
