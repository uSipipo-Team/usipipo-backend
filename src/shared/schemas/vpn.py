"""Schemas para VPN."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field
from usipipo_commons.domain.enums.key_status import KeyStatus
from usipipo_commons.domain.enums.key_type import KeyType


class VpnKeyResponse(BaseModel):
    """Respuesta de clave VPN."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    key_type: KeyType
    status: KeyStatus = KeyStatus.ACTIVE
    config: str | None = None
    created_at: datetime
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    data_used_gb: float = 0.0
    data_limit_gb: float

    @property
    @computed_field
    def vpn_type(self) -> KeyType:
        """Alias para key_type (compatibilidad con API)."""
        return self.key_type


class CreateVpnKeyRequest(BaseModel):
    """Solicitud para crear clave VPN."""

    name: str = Field(..., min_length=1, max_length=50, description="Nombre de la clave")
    vpn_type: KeyType = Field(..., description="Tipo de VPN")
    data_limit_gb: float = Field(default=5.0, ge=0.1, le=100.0, description="Límite de datos en GB")


class UpdateVpnKeyRequest(BaseModel):
    """Solicitud para actualizar clave VPN."""

    name: str | None = Field(None, min_length=1, max_length=50)
    data_limit_gb: float | None = Field(None, ge=0.1, le=100.0)
