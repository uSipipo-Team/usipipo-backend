"""Usage sync job - Syncs VPN usage data from servers every 30 minutes."""

import logging
from datetime import UTC, datetime

from src.core.application.services.vpn_infrastructure_service import (
    VpnInfrastructureService,
)
from src.core.domain.interfaces.i_vpn_key_repository import IVpnKeyRepository

logger = logging.getLogger(__name__)


async def sync_vpn_usage_job(
    key_repo: IVpnKeyRepository,
    vpn_infra_service: VpnInfrastructureService,
) -> dict:
    """
    Job que sincroniza el uso de datos desde los servidores VPN.

    Ejecuta cada 30 minutos para mantener actualizado el consumo de datos.

    Args:
        key_repo: Repositorio de claves VPN
        vpn_infra_service: Servicio de infraestructura VPN

    Returns:
        Dict con {"synced": int, "failed": int, "errors": list, "total_bytes_synced": int}
    """
    logger.info("Starting VPN usage sync job...")

    try:
        # Obtener todas las claves activas
        all_keys = await key_repo.get_all_active()

        synced = 0
        failed = 0
        errors = []
        total_bytes_synced = 0

        for key in all_keys:
            try:
                # Obtener uso real desde el servidor VPN
                usage = await vpn_infra_service.get_key_usage_from_server(key.id, key.vpn_type)
                bytes_used = usage.get("bytes_used", 0)

                # Convertir a GB
                data_used_gb = bytes_used / (1024**3)

                # Actualizar en BD
                updated_key = key
                updated_key.data_used_gb = data_used_gb
                updated_key.last_used_at = datetime.now(UTC) if bytes_used > 0 else key.last_used_at

                await key_repo.update(updated_key)
                synced += 1
                total_bytes_synced += bytes_used

                logger.debug(
                    f"Synced key {key.id} (user: {key.user_id}): "
                    f"{data_used_gb:.2f} GB ({bytes_used} bytes)"
                )

            except Exception as e:
                failed += 1
                errors.append(f"Key {key.id}: {str(e)}")
                logger.error(f"Failed to sync key {key.id}: {e}")

        result = {
            "timestamp": datetime.now(UTC).isoformat(),
            "synced": synced,
            "failed": failed,
            "errors": errors,
            "total_bytes_synced": total_bytes_synced,
            "total_gb_synced": round(total_bytes_synced / (1024**3), 2),
        }

        logger.info(f"VPN usage sync job completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in sync_vpn_usage_job: {e}")
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "synced": 0,
            "failed": 0,
            "errors": [str(e)],
            "total_bytes_synced": 0,
            "total_gb_synced": 0,
        }
