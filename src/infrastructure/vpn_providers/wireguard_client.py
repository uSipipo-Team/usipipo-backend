"""Cliente de infraestructura para WireGuard nativo."""

import asyncio
import ipaddress
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from src.shared.config import settings


class WireGuardClient:
    """
    Cliente de infraestructura para gestionar WireGuard nativo.
    Portado desde la implementación estable en usipipobot.
    """

    def __init__(
        self,
        interface: str | None = None,
        base_path: str | None = None,
        server_port: int | None = None,
        server_ip: str | None = None,
        client_dns: str | None = None,
    ):
        """
        Inicializa el cliente de WireGuard.

        Args:
            interface: Nombre de la interfaz (por defecto de settings)
            base_path: Path al directorio de WireGuard
            server_port: Puerto del servidor WireGuard
            server_ip: IP pública del servidor
            client_dns: DNS para clientes
        """
        self.interface = interface or settings.WG_INTERFACE
        self.base_path = Path(base_path or settings.WG_PATH)
        self.conf_path = self.base_path / f"{self.interface}.conf"
        self.clients_dir = self.base_path / "clients"
        self.server_port = server_port or settings.WG_SERVER_PORT
        self.server_ip = server_ip or settings.SERVER_IP
        self.client_dns = client_dns or settings.WG_CLIENT_DNS_1
        self._permissions_checked = False
        self._usage_cache: tuple[list[dict], datetime] | None = None
        self._cache_ttl = timedelta(seconds=10)
        self._cache_lock = asyncio.Lock()

        self.clients_dir.mkdir(parents=True, exist_ok=True)

    async def _run_cmd(self, cmd: str, retries: int = 2) -> str:
        """
        Ejecuta comandos de WireGuard con reintentos.

        Args:
            cmd: Comando a ejecutar
            retries: Número de reintentos para errores transitorios

        Returns:
            Output del comando

        Raises:
            PermissionError: Si no hay permisos
            Exception: Si hay error en el comando
        """

        def run_sync() -> str:
            # nosec B602 - subprocess con shell=True es necesario para comandos wg
            # Los comandos son construidos internamente, no hay input de usuario
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # nosec B602
            if result.returncode != 0:
                error_msg = result.stderr.strip() or f"Exit code: {result.returncode}"

                if "Operation not permitted" in error_msg:
                    raise PermissionError(
                        "WireGuard requiere CAP_NET_ADMIN. "
                        "Ejecuta: sudo setcap cap_net_admin+ep /usr/bin/wg"
                    )
                raise Exception(f"Error ejecutando comando WireGuard: {error_msg}")
            return result.stdout.strip()

        last_error = None

        for attempt in range(retries + 1):
            try:
                return await asyncio.to_thread(run_sync)
            except PermissionError:
                raise
            except Exception as e:
                last_error = e
                if attempt < retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue

        raise last_error or Exception("Error ejecutando comando WireGuard")

    async def _check_permissions(self) -> bool:
        """Verifica si tenemos permisos para gestionar WireGuard."""
        try:
            await self._run_cmd(f"wg show {self.interface}")
            return True
        except PermissionError:
            return False
        except Exception:
            return True

    async def ensure_permissions(self) -> None:
        """Verifica permisos una sola vez al primer uso."""
        if not self._permissions_checked:
            if not await self._check_permissions():
                raise PermissionError(
                    "WireGuard no tiene permisos. Ejecuta:\n"
                    "sudo setcap cap_net_admin+ep /usr/bin/wg"
                )
            self._permissions_checked = True

    async def get_next_available_ip(self) -> str:
        """
        Obtiene la siguiente IP disponible en la red WireGuard.

        Returns:
            IP disponible (ej: 10.0.0.2)

        Raises:
            Exception: Si no se puede leer la configuración
        """
        content = self.conf_path.read_text()
        addr_match = re.search(r"Address\s*=\s*([\d.]+)", content)
        if not addr_match:
            raise Exception("No se encontró la dirección base en wg0.conf")

        network = ipaddress.IPv4Network(f"{addr_match.group(1)}/24", strict=False)
        existing_ips = set()

        for match in re.finditer(r"AllowedIPs\s*=\s*([\d.]+/32)", content):
            existing_ips.add(match.group(1))

        for host in network.hosts():
            ip = f"{host}/32"
            if ip not in existing_ips:
                return str(host)

        raise Exception("No hay IPs disponibles en la red WireGuard")

    async def create_peer(self, client_name: str) -> dict:
        """
        Crea un nuevo peer WireGuard.

        Args:
            client_name: Nombre del cliente

        Returns:
            Dict con id, name, client_name, ip, config, file_path

        Raises:
            Exception: Si hay error al crear el peer
        """
        await self.ensure_permissions()

        client_ip = await self.get_next_available_ip()
        client_name_safe = re.sub(r"[^a-zA-Z0-9_-]", "_", client_name)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_name = f"{self.interface}-{client_name_safe}-{timestamp}"

        # nosec B108 - /tmp es seguro para archivos temporales con nombres únicos
        # El archivo tiene permisos 0o600 y se elimina inmediatamente después del uso
        psk_file_path = f"/tmp/psk_{unique_name}.txt"  # nosec B108

        try:
            priv_key_output = await self._run_cmd("wg genkey")
            priv_key = priv_key_output.strip()

            pub_key_output = await self._run_cmd(f"echo '{priv_key}' | wg pubkey")
            pub_key = pub_key_output.strip()

            psk_output = await self._run_cmd("wg genpsk")
            psk = psk_output.strip()

            psk_file = Path(psk_file_path)
            with psk_file.open("w") as f:
                f.write(psk)
            psk_file.chmod(0o600)

            psk_file_content = Path(psk_file_path).read_text()

            cmd = (
                f"wg set {self.interface} peer {pub_key} "
                f"allowed-ips {client_ip}/32 preshared-key {psk_file_path}"
            )
            await self._run_cmd(cmd)

            server_pub_key_output = await self._run_cmd(f"wg show {self.interface} public-key")
            server_pub_key = server_pub_key_output.strip()

            client_conf = self._build_client_config(
                priv_key=priv_key,
                ip=client_ip,
                server_pub=server_pub_key,
                psk=psk_file_content.strip(),
            )

            client_file = self.clients_dir / f"{self.interface}-{client_name_safe}.conf"
            client_file.write_text(client_conf)
            client_file.chmod(0o600)

            return {
                "id": pub_key,
                "name": client_name,
                "client_name": unique_name,
                "ip": client_ip,
                "config": client_conf,
                "file_path": str(client_file),
            }
        except Exception as e:
            raise Exception(f"Error al crear peer WireGuard: {e}") from e
        finally:
            psk_file = Path(psk_file_path)
            if psk_file.exists():
                psk_file.unlink()

    def _build_client_config(
        self,
        priv_key: str,
        ip: str,
        server_pub: str,
        psk: str,
    ) -> str:
        """
        Construye la configuración del cliente WireGuard.

        Args:
            priv_key: Private key del cliente
            ip: IP asignada al cliente
            server_pub: Public key del servidor
            psk: Pre-shared key

        Returns:
            Configuración en formato WireGuard
        """
        endpoint = f"{self.server_ip}:{self.server_port}"

        return f"""[Interface]
PrivateKey = {priv_key}
Address = {ip}/24
DNS = {self.client_dns}
MTU = 1420

[Peer]
PublicKey = {server_pub}
PresharedKey = {psk}
Endpoint = {endpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 15
"""

    async def delete_peer(self, pub_key: str, client_name: str) -> bool:
        """
        Elimina un peer de WireGuard.

        Args:
            pub_key: Public key del peer
            client_name: Nombre del cliente

        Returns:
            True si se eliminó
        """
        try:
            content = self.conf_path.read_text()

            pk_pattern = rf"### CLIENT {re.escape(client_name)}.*?PublicKey\s*=\s*([^\n]+)"
            match = re.search(pk_pattern, content, flags=re.DOTALL)

            if match:
                found_pub_key = match.group(1).strip()
                await self._run_cmd(f"wg set {self.interface} peer {found_pub_key} remove")
            elif pub_key:
                await self._run_cmd(f"wg set {self.interface} peer {pub_key} remove")

            pattern = rf"### CLIENT {re.escape(client_name)}.*?(?=\n### CLIENT|\Z)"
            new_content = re.sub(pattern, "", content, flags=re.DOTALL)
            self.conf_path.write_text(new_content.strip() + "\n")

            client_file = self.clients_dir / f"{self.interface}-{client_name}.conf"
            if client_file.exists():
                client_file.unlink()

            return True
        except Exception:
            return False

    async def delete_client(self, client_name: str) -> bool:
        """
        Elimina un cliente WireGuard.

        Args:
            client_name: Nombre del cliente

        Returns:
            True si se eliminó
        """
        return await self.delete_peer(pub_key="", client_name=client_name)

    async def get_peer_metrics(self, client_name: str) -> dict[str, int]:
        """
        Obtiene métricas para un cliente específico.

        Args:
            client_name: Nombre del cliente

        Returns:
            Dict con transfer_rx, transfer_tx, transfer_total
        """
        try:
            if not self.conf_path.exists():
                return {"transfer_total": 0, "transfer_rx": 0, "transfer_tx": 0}

            content = self.conf_path.read_text()

            pk_pattern = rf"### CLIENT {re.escape(client_name)}.*?PublicKey\s*=\s*([^\n]+)"
            match = re.search(pk_pattern, content, flags=re.DOTALL)

            if not match:
                return {"transfer_total": 0, "transfer_rx": 0, "transfer_tx": 0}

            target_pub_key = match.group(1).strip()
            all_usage = await self.get_usage()

            for peer in all_usage:
                if peer["public_key"] == target_pub_key:
                    return {
                        "transfer_rx": peer["rx"],
                        "transfer_tx": peer["tx"],
                        "transfer_total": peer["total"],
                    }

            return {"transfer_total": 0, "transfer_rx": 0, "transfer_tx": 0}
        except Exception:
            return {"transfer_total": 0, "transfer_rx": 0, "transfer_tx": 0}

    async def get_usage(self) -> list[dict]:
        """
        Obtiene métricas de uso de todos los peers con caching.

        Returns:
            Lista de dicts con public_key, rx, tx, total
        """
        async with self._cache_lock:
            if self._usage_cache is not None:
                cached_data, cached_time = self._usage_cache
                if datetime.now() - cached_time < self._cache_ttl:
                    return cached_data

            try:
                output = await self._run_cmd(f"wg show {self.interface} dump")
                lines = output.split("\n")[1:]

                usage = []
                for line in lines:
                    cols = line.split("\t")
                    if len(cols) >= 7:
                        usage.append(
                            {
                                "public_key": cols[0],
                                "rx": int(cols[5]),
                                "tx": int(cols[6]),
                                "total": int(cols[5]) + int(cols[6]),
                            }
                        )

                self._usage_cache = (usage, datetime.now())
                return usage
            except Exception:
                return []

    async def disable_peer(self, client_name: str) -> bool:
        """
        Deshabilita un peer sin eliminarlo (bloquea tráfico).

        Args:
            client_name: Nombre del cliente

        Returns:
            True si se deshabilitó
        """
        try:
            if not self.conf_path.exists():
                return False

            content = self.conf_path.read_text()

            pk_pattern = rf"### CLIENT {re.escape(client_name)}.*?PublicKey\s*=\s*([^\n]+)"
            match = re.search(pk_pattern, content, flags=re.DOTALL)

            if not match:
                return False

            pub_key = match.group(1).strip()

            await self._run_cmd(f"wg set {self.interface} peer {pub_key} allowed-ips 0.0.0.0/32")

            new_content = content.replace(
                f"### CLIENT {client_name}",
                f"### CLIENT {client_name} [DISABLED]",
            )
            self.conf_path.write_text(new_content)

            return True
        except Exception:
            return False

    async def enable_peer(self, client_name: str) -> bool:
        """
        Habilita un peer previamente deshabilitado.

        Args:
            client_name: Nombre del cliente

        Returns:
            True si se habilitó
        """
        try:
            if not self.conf_path.exists():
                return False

            content = self.conf_path.read_text()

            # Buscar el peer por client_name (puede estar deshabilitado)
            pk_pattern = rf"### CLIENT {re.escape(client_name)}.*?PublicKey\s*=\s*([^\n]+)"
            match = re.search(pk_pattern, content, flags=re.DOTALL)

            if not match:
                return False

            pub_key = match.group(1).strip()

            # Leer la IP permitida original desde el archivo del cliente
            client_file = self.clients_dir / f"{self.interface}-{client_name}.conf"
            if not client_file.exists():
                return False

            client_content = client_file.read_text()
            ip_match = re.search(r"Address\s*=\s*([\d.]+)", client_content)

            if not ip_match:
                return False

            client_ip = ip_match.group(1)

            # Restaurar AllowedIPs original
            await self._run_cmd(
                f"wg set {self.interface} peer {pub_key} allowed-ips {client_ip}/32"
            )

            # Remover marca [DISABLED] del comentario
            new_content = content.replace(
                f"### CLIENT {client_name} [DISABLED]",
                f"### CLIENT {client_name}",
            )
            self.conf_path.write_text(new_content)

            return True
        except Exception:
            return False
