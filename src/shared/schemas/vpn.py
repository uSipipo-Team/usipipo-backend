"""Schemas para VPN."""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID

from usipipo_commons.domain.enums.vpn_type import VpnType
from usipipo_commons.domain.enums.key_status import KeyStatus


class VpnKeyResponse(BaseModel):
    """Respuesta de clave VPN."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    vpn_type: VpnType
    status: KeyStatus
    config: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    data_used_gb: float
    data_limit_gb: float


class CreateVpnKeyRequest(BaseModel):
    """Solicitud para crear clave VPN."""

    name: str = Field(
        ..., min_length=1, max_length=50, description="Nombre de la clave"
    )
    vpn_type: VpnType = Field(..., description="Tipo de VPN")
    data_limit_gb: float = Field(
        default=5.0, ge=0.1, le=100.0, description="Límite de datos en GB"
    )


class UpdateVpnKeyRequest(BaseModel):
    """Solicitud para actualizar clave VPN."""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    data_limit_gb: Optional[float] = Field(None, ge=0.1, le=100.0)
