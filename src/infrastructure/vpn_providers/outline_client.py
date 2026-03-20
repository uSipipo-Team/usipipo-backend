"""Cliente de infraestructura para la API de Outline (Shadowbox)."""

from urllib.parse import quote

import httpx

from src.shared.config import settings


class OutlineClient:
    """
    Cliente de infraestructura para la API de Outline (Shadowbox).
    Portado desde la implementación estable en usipipobot.
    """

    def __init__(
        self,
        api_url: str | None = None,
        verify_ssl: bool = False,
        timeout: float = 15.0,
    ):
        """
        Inicializa el cliente de Outline.

        Args:
            api_url: URL de la API de Outline (por defecto de settings)
            verify_ssl: Verificar certificados SSL (False para autofirmados)
            timeout: Timeout para requests en segundos
        """
        self.api_url = api_url or settings.OUTLINE_API_URL
        self.brand = "uSipipo VPN"
        self.client = httpx.AsyncClient(
            verify=verify_ssl,
            timeout=timeout,
        )

    @staticmethod
    def apply_branding(access_url: str, brand_name: str) -> str:
        """
        Añade el tag de branding al final de la URL ss://

        Args:
            access_url: URL de acceso ss://...
            brand_name: Nombre de la marca

        Returns:
            URL con branding aplicado
        """
        tag = quote(brand_name)
        return f"{access_url}#{tag}"

    async def get_server_info(self) -> dict:
        """
        Obtiene estado de salud y estadísticas básicas del servidor.

        Returns:
            Dict con información del servidor
        """
        try:
            server_res = await self.client.get(f"{self.api_url}/server")
            keys_res = await self.client.get(f"{self.api_url}/access-keys")

            server_res.raise_for_status()

            data = server_res.json()
            keys_data = keys_res.json()

            return {
                "name": data.get("name", "Outline Server"),
                "server_id": data.get("serverId"),
                "version": data.get("version"),
                "total_keys": len(keys_data.get("accessKeys", [])),
                "is_healthy": True,
            }
        except Exception as e:
            return {"is_healthy": False, "error": str(e)}

    async def create_key(self, name: str = "Usuario") -> dict:
        """
        Crea una llave, la renombra y aplica branding.

        Args:
            name: Nombre para la clave VPN

        Returns:
            Dict con id, name, access_url, port, method

        Raises:
            Exception: Si hay error al generar acceso
        """
        try:
            # 1. Crear la llave
            res = await self.client.post(f"{self.api_url}/access-keys")
            res.raise_for_status()
            key_data = res.json()

            key_id = key_data["id"]

            # 2. Renombrar la llave
            await self.client.put(
                f"{self.api_url}/access-keys/{key_id}/name",
                data={"name": name},
            )

            # 3. Formatear respuesta con branding
            return {
                "id": key_id,
                "name": name,
                "access_url": self.apply_branding(key_data["accessUrl"], self.brand),
                "port": key_data.get("port"),
                "method": key_data.get("method"),
            }
        except Exception as e:
            raise Exception("Error al generar acceso en el servidor VPN.") from e

    async def delete_key(self, key_id: str) -> bool:
        """
        Elimina una llave. Retorna True incluso si ya no existe (404).

        Args:
            key_id: ID de la clave a eliminar

        Returns:
            True si se eliminó o ya no existía
        """
        try:
            res = await self.client.delete(f"{self.api_url}/access-keys/{key_id}")
            if res.status_code == 404:
                return True
            return res.status_code == 204
        except Exception:
            return False

    async def get_metrics(self) -> dict[str, int]:
        """
        Obtiene el mapa completo de consumo de datos del servidor.

        Returns:
            Dict { key_id: bytes_usados }
        """
        try:
            res = await self.client.get(f"{self.api_url}/metrics/transfer")
            return res.json().get("bytesTransferredByUserId", {})
        except Exception:
            return {}

    async def get_key_usage(self, key_id: str) -> dict:
        """
        Obtiene consumo de datos de una clave específica.

        Args:
            key_id: ID de la clave

        Returns:
            Dict con bytes_used, bytes_rx, bytes_tx
        """
        try:
            res = await self.client.get(f"{self.api_url}/metrics/transfer")
            usage_map = res.json().get("bytesTransferredByUserId", {})

            bytes_used = usage_map.get(key_id, 0)

            return {
                "bytes_used": bytes_used,
                "bytes_rx": 0,  # Outline no separa RX/TX
                "bytes_tx": 0,
            }
        except Exception:
            return {"bytes_used": 0, "bytes_rx": 0, "bytes_tx": 0}

    async def disable_key(self, key_id: str) -> bool:
        """
        Deshabilita una clave estableciendo un límite de datos de 1 byte.

        Args:
            key_id: ID de la clave a deshabilitar

        Returns:
            True si se deshabilitó
        """
        try:
            # Establecer data-limit a 1 byte efectivamente bloquea el tráfico
            res = await self.client.put(
                f"{self.api_url}/access-keys/{key_id}/data-limit",
                json={"limit": 1},  # 1 byte = efectivamente bloqueado
            )
            return res.status_code == 201
        except Exception:
            return False

    async def enable_key(self, key_id: str) -> bool:
        """
        Habilita una clave removiendo el límite de datos.

        Args:
            key_id: ID de la clave a habilitar

        Returns:
            True si se habilitó
        """
        try:
            # Remover el data-limit establece la clave como ilimitada
            res = await self.client.delete(f"{self.api_url}/access-keys/{key_id}/data-limit")
            return res.status_code == 204
        except Exception:
            return False

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        await self.client.aclose()

    async def __aenter__(self) -> "OutlineClient":
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        await self.close()
