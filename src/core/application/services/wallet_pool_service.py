"""Servicio de aplicación para gestión de pool de wallets reutilizables."""

from datetime import datetime, timedelta
from uuid import UUID

from usipipo_commons.domain.entities.wallet import WalletPool
from usipipo_commons.domain.interfaces.i_wallet_pool_repository import IWalletPoolRepository

from src.core.domain.interfaces.i_crypto_order_repository import ICryptoOrderRepository
from src.infrastructure.api_clients.client_tron_dealer import (
    BscWallet,
    TronDealerApiError,
    TronDealerClient,
)
from src.infrastructure.api_clients.client_tron_dealer import (
    WalletStatus as TronWalletStatus,
)


class WalletPoolService:
    """
    Servicio para gestionar un pool de wallets reutilizables.

    Estrategia:
    1. Primero busca wallets expiradas del mismo usuario
    2. Si no hay, busca cualquier wallet expirada no en uso
    3. Si no hay disponibles, crea una nueva wallet
    """

    def __init__(
        self,
        tron_dealer_client: TronDealerClient,
        wallet_pool_repo: IWalletPoolRepository,
        crypto_order_repo: ICryptoOrderRepository,
    ):
        self.tron_dealer_client = tron_dealer_client
        self.wallet_pool_repo = wallet_pool_repo
        self.crypto_order_repo = crypto_order_repo

    async def get_or_assign_wallet(
        self,
        user_id: UUID,
        telegram_id: int,
        label: str | None = None,
    ) -> BscWallet | None:
        """
        Obtiene una wallet para el usuario, reutilizando si es posible.

        Args:
            user_id: UUID del usuario
            telegram_id: Telegram ID del usuario
            label: Label opcional para la wallet

        Returns:
            BscWallet: Wallet existente reutilizada o nueva
        """
        try:
            # Paso 1: Buscar wallet reutilizable del mismo usuario
            reusable_wallet = await self.wallet_pool_repo.get_reusable_for_user(user_id)

            if reusable_wallet:
                # Marcar como reutilizada
                reusable_wallet.mark_reused(user_id)
                await self.wallet_pool_repo.update(reusable_wallet)

                return BscWallet(
                    id="reused",
                    address=reusable_wallet.wallet_address,
                    label=label or f"user-{telegram_id}",
                    status=TronWalletStatus.ACTIVE,
                )

            # Paso 2: Buscar cualquier wallet expirada no en uso
            any_reusable = await self.wallet_pool_repo.get_any_available()

            if any_reusable:
                # Marcar como reutilizada
                any_reusable.mark_reused(user_id)
                await self.wallet_pool_repo.update(any_reusable)

                return BscWallet(
                    id="reused",
                    address=any_reusable.wallet_address,
                    label=label or f"user-{telegram_id}",
                    status=TronWalletStatus.ACTIVE,
                )

            # Paso 3: Crear nueva wallet si no hay reutilizables
            return await self._create_new_wallet(user_id, telegram_id, label)

        except Exception as e:
            print(f"Error en get_or_assign_wallet para user {telegram_id}: {e}")
            return None

    async def _create_new_wallet(
        self,
        user_id: UUID,
        telegram_id: int,
        label: str | None = None,
    ) -> BscWallet | None:
        """Crea una nueva wallet para el usuario."""
        try:
            async with self.tron_dealer_client as client:
                wallet = await client.assign_wallet(label=label or f"user-{telegram_id}")

            return wallet

        except TronDealerApiError as e:
            if e.status_code == 401:
                print(f"TronDealer API authentication failed for user {telegram_id}")
            else:
                print(f"TronDealer API error {e.status_code} for user {telegram_id}: {e.message}")
            return None
        except Exception as e:
            print(f"Unexpected error creating wallet for user {telegram_id}: {e}")
            return None

    async def add_to_pool(
        self,
        wallet_address: str,
        user_id: UUID,
        expires_at: datetime | None = None,
    ) -> WalletPool:
        """
        Agrega una wallet expirada al pool para reutilización.

        Args:
            wallet_address: Dirección de la wallet
            user_id: UUID del usuario original
            expires_at: Fecha de expiración (por defecto 24 horas)

        Returns:
            WalletPool creada
        """
        if expires_at is None:
            expires_at = datetime.utcnow() + timedelta(hours=24)

        pool_entry = WalletPool.create(
            wallet_address=wallet_address,
            original_user_id=user_id,
            expires_at=expires_at,
        )

        return await self.wallet_pool_repo.create(pool_entry)

    async def cleanup_expired(self) -> int:
        """
        Limpia wallets expiradas del pool.

        Returns:
            Cantidad de entradas eliminadas
        """
        return await self.wallet_pool_repo.cleanup_expired()

    async def get_pool_stats(self) -> dict:
        """
        Obtiene estadísticas del pool.

        Returns:
            Diccionario con estadísticas del pool
        """
        all_wallets = await self.wallet_pool_repo.get_all()
        available = await self.wallet_pool_repo.get_available_wallets()
        expired = await self.wallet_pool_repo.get_expired_wallets()

        return {
            "total": len(all_wallets),
            "available": len(available),
            "expired": len(expired),
            "in_use": len(all_wallets) - len(available) - len(expired),
        }
