"""Crypto payment service for managing cryptocurrency payments."""

import logging
from uuid import UUID

from usipipo_commons.domain.entities.crypto_order import CryptoOrder
from usipipo_commons.domain.entities.crypto_transaction import (
    CryptoTransaction,
)

from src.core.application.exceptions import UserNotFoundError
from src.core.application.services.payment_service import PaymentService
from src.core.domain.interfaces.i_crypto_order_repository import ICryptoOrderRepository
from src.core.domain.interfaces.i_crypto_transaction_repository import (
    ICryptoTransactionRepository,
)
from src.core.domain.interfaces.i_user_repository import IUserRepository

logger = logging.getLogger(__name__)

REQUIRED_CONFIRMATIONS = 15


class CryptoPaymentService:
    """Service for managing cryptocurrency payments with blockchain confirmations."""

    def __init__(
        self,
        crypto_order_repo: ICryptoOrderRepository,
        crypto_transaction_repo: ICryptoTransactionRepository,
        user_repo: IUserRepository,
        payment_service: PaymentService,
    ):
        self.crypto_order_repo = crypto_order_repo
        self.crypto_transaction_repo = crypto_transaction_repo
        self.user_repo = user_repo
        self.payment_service = payment_service

    async def create_order(
        self,
        user_id: UUID,
        package_type: str,
        amount_usdt: float,
        wallet_address: str,
    ) -> CryptoOrder:
        """Creates a new crypto order."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        order = CryptoOrder.create(
            user_id=user_id,
            package_type=package_type,
            amount_usdt=amount_usdt,
            wallet_address=wallet_address,
        )

        saved_order = await self.crypto_order_repo.save(order)

        logger.info(
            f"Created crypto order {saved_order.id} for user {user_id}: "
            f"{amount_usdt} USDT to {wallet_address}"
        )

        return saved_order

    async def process_webhook_payment(
        self,
        wallet_address: str,
        amount: float,
        tx_hash: str,
        token_symbol: str,
        raw_payload: dict,
        confirmations: int = 0,
    ) -> CryptoTransaction | None:
        """
        Processes a payment webhook from blockchain.

        Args:
            wallet_address: Wallet address that received the payment
            amount: Amount received
            tx_hash: Transaction hash
            token_symbol: Token symbol (e.g., USDT)
            raw_payload: Raw webhook payload
            confirmations: Number of blockchain confirmations

        Returns:
            CryptoTransaction if processed, None if ignored
        """
        # Check if transaction already exists
        existing = await self.crypto_transaction_repo.get_by_tx_hash(tx_hash)
        if existing:
            logger.info(f"Transaction already processed: {tx_hash}")
            return existing

        # If not enough confirmations, keep as pending
        if confirmations < REQUIRED_CONFIRMATIONS:
            logger.info(
                f"Transaction {tx_hash} has {confirmations} confirmations, "
                f"need {REQUIRED_CONFIRMATIONS}. Keeping as pending."
            )

            transaction = CryptoTransaction.create(
                wallet_address=wallet_address,
                amount=amount,
                tx_hash=tx_hash,
                token_symbol=token_symbol,
                raw_payload=raw_payload,
            )
            transaction.confirmations = confirmations

            return await self.crypto_transaction_repo.save(transaction)

        # Find order by wallet address
        order = await self.crypto_order_repo.get_by_wallet(wallet_address)

        # Find user by wallet address (if no order)
        user_id = await self._find_user_by_wallet(wallet_address)

        if not user_id:
            logger.warning(f"No user found for wallet: {wallet_address}")
            if order:
                await self.crypto_order_repo.mark_failed(order.id)
            return None

        # Create confirmed transaction
        transaction = CryptoTransaction.create(
            wallet_address=wallet_address,
            amount=amount,
            tx_hash=tx_hash,
            token_symbol=token_symbol,
            raw_payload=raw_payload,
        )
        transaction.user_id = user_id
        transaction.confirmations = confirmations
        transaction.confirm()

        saved_transaction = await self.crypto_transaction_repo.save(transaction)

        # Complete the payment
        if order:
            await self.crypto_order_repo.mark_completed(order.id, tx_hash)

        return saved_transaction

    async def _find_user_by_wallet(self, wallet_address: str) -> UUID | None:
        """
        Finds user by wallet address.

        This is a placeholder. In production, you would:
        1. Check a user_wallets table
        2. Or derive from order history
        3. Or use a wallet-to-user mapping service
        """
        # TODO: Implement wallet-to-user mapping
        # For now, try to find through orders
        order = await self.crypto_order_repo.get_by_wallet(wallet_address)
        if order:
            return order.user_id

        return None

    async def get_user_orders(self, user_id: UUID, limit: int = 50) -> list[CryptoOrder]:
        """Gets crypto orders for a user."""
        return await self.crypto_order_repo.get_by_user_id(user_id, limit)

    async def get_user_transactions(
        self, user_id: UUID, limit: int = 50
    ) -> list[CryptoTransaction]:
        """Gets crypto transactions for a user."""
        return await self.crypto_transaction_repo.get_by_user_id(user_id, limit)
