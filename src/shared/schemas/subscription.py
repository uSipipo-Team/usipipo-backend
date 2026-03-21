"""Schemas para suscripciones."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from usipipo_commons.domain.entities.subscription_plan import PlanType


class SubscriptionPlanResponse(BaseModel):
    """Respuesta de plan de suscripción disponible."""

    name: str = Field(..., description="Nombre del plan (e.g., '1 Month', '3 Months')")
    plan_type: PlanType = Field(..., description="Tipo de plan")
    duration_months: int = Field(..., description="Duración en meses")
    stars: int = Field(..., description="Cantidad de Stars requeridos")
    usdt: float = Field(..., description="Precio en USDT")
    data_limit: str = Field(default="Unlimited", description="Límite de datos")
    bonus_percent: int = Field(default=0, description="Porcentaje de bonus/descuento")


class UserSubscriptionResponse(BaseModel):
    """Respuesta de suscripción actual del usuario."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: int
    plan_type: PlanType
    stars_paid: int
    payment_id: str
    starts_at: datetime
    expires_at: datetime
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    days_remaining: int | None = None
    is_expiring_soon: bool | None = None
    is_expired: bool | None = None


class ActivateSubscriptionRequest(BaseModel):
    """Solicitud para activar suscripción."""

    plan_type: str = Field(..., description="Tipo de plan (one_month, three_months, six_months)")
    payment_id: str = Field(..., description="ID del pago (para idempotencia)")


class ActivateSubscriptionResponse(BaseModel):
    """Respuesta de activación de suscripción."""

    success: bool = Field(..., description="Si la activación fue exitosa")
    subscription_id: UUID = Field(..., description="ID de la suscripción activada")
    plan_type: PlanType = Field(..., description="Tipo de plan activado")
    expires_at: datetime = Field(..., description="Fecha de expiración")
    message: str | None = Field(None, description="Mensaje adicional")
