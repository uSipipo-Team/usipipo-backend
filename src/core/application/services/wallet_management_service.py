"""Servicio de aplicación para gestión de wallets BSC."""

from uuid import UUID

from usipipo_commons.domain.entities.wallet import Wallet
from usipipo_commons.domain.enums.wallet_status import WalletStatus
from usipipo_commons.domain.interfaces.i_wallet_repository import IWalletRepository

from src.core.domain.interfaces.i_user_repository import IUserRepository
from src.infrastructure.api_clients.client_tron_dealer import (
    BscWallet,
    TronDealerApiError,
    TronDealerClient,
)
from src.infrastructure.api_clients.client_tron_dealer import (
    WalletStatus as TronWalletStatus,
)


class WalletManagementService:
    """
    Servicio para gestionar operaciones de wallets BSC mediante TronDealer API.

    Incluye soporte para reutilización de wallets mediante WalletPoolService.
    """

    def __init__(
        self,
        tron_dealer_client: TronDealerClient,
        wallet_repo: IWalletRepository,
        user_repo: IUserRepository,
    ):
        self.tron_dealer_client = tron_dealer_client
        self.wallet_repo = wallet_repo
        self.user_repo = user_repo

    async def assign_wallet(
        self,
        user_id: UUID,
        telegram_id: int,
        label: str | None = None,
    ) -> BscWallet | None:
        """
        Asigna una wallet BSC a un usuario.

        Intenta reutilizar wallets expiradas antes de crear una nueva.

        Args:
            user_id: UUID del usuario
            telegram_id: Telegram ID del usuario
            label: Label opcional para la wallet

        Returns:
            BscWallet: Wallet reutilizada o nueva, o None si falló
        """
        try:
            # Intentar reutilizar wallet del pool primero
            reused_address = await self.wallet_repo.get_reusable_wallet_for_user(user_id)

            if reused_address:
                # Verificar que no exista ya en la base de datos
                existing = await self.wallet_repo.get_by_address(reused_address)
                if not existing:
                    # Crear entrada de wallet reutilizada
                    wallet_entity = Wallet.create(
                        user_id=user_id,
                        address=reused_address,
                        label=label or f"user-{telegram_id}",
                    )
                    wallet_entity.status = WalletStatus.ACTIVE
                    await self.wallet_repo.create(wallet_entity)

                    return BscWallet(
                        id="reused",
                        address=reused_address,
                        label=label or f"user-{telegram_id}",
                        status=TronWalletStatus.ACTIVE,
                    )

            # Crear nueva wallet si no hay reutilizables
            async with self.tron_dealer_client as client:
                new_wallet = await client.assign_wallet(label=label or f"user-{telegram_id}")

            # Guardar wallet en repositorio
            wallet_entity = Wallet.create(
                user_id=user_id,
                address=new_wallet.address,
                label=new_wallet.label,
            )
            await self.wallet_repo.create(wallet_entity)

            return new_wallet

        except TronDealerApiError as e:
            if e.status_code == 401:
                print(f"TronDealer API authentication failed for user {telegram_id}")
            else:
                print(f"TronDealer API error {e.status_code} for user {telegram_id}: {e.message}")
            return None
        except Exception as e:
            print(f"Unexpected error assigning wallet to user {telegram_id}: {e}")
            return None

    async def get_wallet(self, user_id: UUID) -> Wallet | None:
        """
        Obtiene la wallet de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Wallet o None si no existe
        """
        return await self.wallet_repo.get_by_user_id(user_id)

    async def get_wallet_by_address(self, address: str) -> Wallet | None:
        """
        Obtiene wallet por dirección.

        Args:
            address: Dirección de la wallet

        Returns:
            Wallet o None si no existe
        """
        return await self.wallet_repo.get_by_address(address)

    async def deactivate_wallet(self, wallet_id: UUID) -> bool:
        """
        Desactiva una wallet.

        Args:
            wallet_id: UUID de la wallet

        Returns:
            True si se desactivó, False si no existía
        """
        wallet = await self.wallet_repo.get_by_id(wallet_id)
        if not wallet:
            return False

        wallet.deactivate()
        await self.wallet_repo.update(wallet)
        return True

    async def activate_wallet(self, wallet_id: UUID) -> bool:
        """
        Activa una wallet.

        Args:
            wallet_id: UUID de la wallet

        Returns:
            True si se activó, False si no existía
        """
        wallet = await self.wallet_repo.get_by_id(wallet_id)
        if not wallet:
            return False

        wallet.activate()
        await self.wallet_repo.update(wallet)
        return True

    async def update_balance(
        self,
        wallet_id: UUID,
        amount_usdt: float,
    ) -> Wallet | None:
        """
        Actualiza el balance de una wallet.

        Args:
            wallet_id: UUID de la wallet
            amount_usdt: Monto a actualizar (positivo para depósito, negativo para retiro)

        Returns:
            Wallet actualizada o None si no existía
        """
        wallet = await self.wallet_repo.get_by_id(wallet_id)
        if not wallet:
            return None

        wallet.update_balance(amount_usdt)
        return await self.wallet_repo.update(wallet)
