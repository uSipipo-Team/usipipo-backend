"""Tests unitarios para WalletManagementService."""

import uuid
from unittest.mock import AsyncMock

import pytest
from usipipo_commons.domain.entities.wallet import Wallet
from usipipo_commons.domain.enums.wallet_status import WalletStatus

from src.core.application.services.wallet_management_service import WalletManagementService
from src.infrastructure.api_clients.client_tron_dealer import (
    BscWallet,
    TronDealerApiError,
)
from src.infrastructure.api_clients.client_tron_dealer import (
    WalletStatus as TronWalletStatus,
)


@pytest.fixture
def mock_wallet_repository():
    """Mock de WalletRepository."""
    return AsyncMock()


@pytest.fixture
def mock_user_repository():
    """Mock de IUserRepository."""
    return AsyncMock()


@pytest.fixture
def mock_tron_dealer_client():
    """Mock de TronDealerClient."""
    client = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    return client


@pytest.fixture
def wallet_service(mock_tron_dealer_client, mock_wallet_repository, mock_user_repository):
    """WalletManagementService con mocks."""
    return WalletManagementService(
        tron_dealer_client=mock_tron_dealer_client,
        wallet_repo=mock_wallet_repository,
        user_repo=mock_user_repository,
    )


class TestAssignWallet:
    """Tests para assign_wallet method."""

    @pytest.mark.asyncio
    async def test_assign_wallet_reuses_existing(
        self, wallet_service, mock_wallet_repository, mock_tron_dealer_client
    ):
        """Should reuse wallet from pool if available."""
        user_id = uuid.uuid4()
        telegram_id = 123456

        # Mock reusable wallet
        mock_wallet_repository.get_reusable_wallet_for_user.return_value = (
            "0x1234567890abcdef1234567890abcdef12345678"
        )
        mock_wallet_repository.get_by_address.return_value = None

        # Mock create
        mock_wallet_repository.create.return_value = Wallet.create(
            user_id=user_id,
            address="0x1234567890abcdef1234567890abcdef12345678",
            label=f"user-{telegram_id}",
        )

        wallet = await wallet_service.assign_wallet(user_id, telegram_id)

        assert wallet is not None
        assert wallet.address == "0x1234567890abcdef1234567890abcdef12345678"
        assert wallet.id == "reused"
        mock_wallet_repository.get_reusable_wallet_for_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_assign_wallet_creates_new_when_no_reusable(
        self, wallet_service, mock_wallet_repository, mock_tron_dealer_client
    ):
        """Should create new wallet when no reusable available."""
        user_id = uuid.uuid4()
        telegram_id = 123456

        # No reusable wallets
        mock_wallet_repository.get_reusable_wallet_for_user.return_value = None

        # Mock new wallet from API
        new_wallet = BscWallet(
            id="new-wallet-123",
            address="0xnewwallet123456789012345678901234567890",
            label=f"user-{telegram_id}",
            status=TronWalletStatus.ACTIVE,
        )
        mock_tron_dealer_client.assign_wallet.return_value = new_wallet

        # Mock create
        mock_wallet_repository.create.return_value = Wallet.create(
            user_id=user_id,
            address=new_wallet.address,
            label=new_wallet.label,
        )

        wallet = await wallet_service.assign_wallet(user_id, telegram_id)

        assert wallet is not None
        assert wallet.address == "0xnewwallet123456789012345678901234567890"
        mock_tron_dealer_client.assign_wallet.assert_called_once()

    @pytest.mark.asyncio
    async def test_assign_wallet_handles_api_error(
        self, wallet_service, mock_wallet_repository, mock_tron_dealer_client
    ):
        """Should handle TronDealer API errors."""
        user_id = uuid.uuid4()
        telegram_id = 123456

        mock_wallet_repository.get_reusable_wallet_for_user.return_value = None

        # Mock API error
        error = TronDealerApiError(status_code=401, message="Authentication failed")
        mock_tron_dealer_client.assign_wallet.side_effect = error

        wallet = await wallet_service.assign_wallet(user_id, telegram_id)

        assert wallet is None


class TestGetWallet:
    """Tests para get_wallet method."""

    @pytest.mark.asyncio
    async def test_get_wallet_by_user_id(self, wallet_service, mock_wallet_repository):
        """Should get wallet by user_id."""
        user_id = uuid.uuid4()

        expected_wallet = Wallet.create(
            user_id=user_id,
            address="0x1234567890abcdef1234567890abcdef12345678",
        )
        mock_wallet_repository.get_by_user_id.return_value = expected_wallet

        wallet = await wallet_service.get_wallet(user_id)

        assert wallet is not None
        assert wallet.user_id == user_id
        mock_wallet_repository.get_by_user_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_wallet_returns_none_when_not_found(
        self, wallet_service, mock_wallet_repository
    ):
        """Should return None when wallet not found."""
        user_id = uuid.uuid4()
        mock_wallet_repository.get_by_user_id.return_value = None

        wallet = await wallet_service.get_wallet(user_id)

        assert wallet is None


class TestDeactivateActivateWallet:
    """Tests para deactivate_wallet and activate_wallet methods."""

    @pytest.mark.asyncio
    async def test_deactivate_wallet(self, wallet_service, mock_wallet_repository):
        """Should deactivate wallet."""
        wallet_id = uuid.uuid4()

        wallet = Wallet.create(
            user_id=uuid.uuid4(),
            address="0x1234567890abcdef1234567890abcdef12345678",
        )
        wallet.status = WalletStatus.ACTIVE

        mock_wallet_repository.get_by_id.return_value = wallet
        mock_wallet_repository.update.return_value = wallet

        result = await wallet_service.deactivate_wallet(wallet_id)

        assert result is True
        assert wallet.status == WalletStatus.INACTIVE
        mock_wallet_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_wallet_returns_false_when_not_found(
        self, wallet_service, mock_wallet_repository
    ):
        """Should return False when wallet not found."""
        wallet_id = uuid.uuid4()
        mock_wallet_repository.get_by_id.return_value = None

        result = await wallet_service.deactivate_wallet(wallet_id)

        assert result is False
        mock_wallet_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_activate_wallet(self, wallet_service, mock_wallet_repository):
        """Should activate wallet."""
        wallet_id = uuid.uuid4()

        wallet = Wallet.create(
            user_id=uuid.uuid4(),
            address="0x1234567890abcdef1234567890abcdef12345678",
        )
        wallet.status = WalletStatus.INACTIVE

        mock_wallet_repository.get_by_id.return_value = wallet
        mock_wallet_repository.update.return_value = wallet

        result = await wallet_service.activate_wallet(wallet_id)

        assert result is True
        assert wallet.status == WalletStatus.ACTIVE


class TestUpdateBalance:
    """Tests para update_balance method."""

    @pytest.mark.asyncio
    async def test_update_balance_deposit(self, wallet_service, mock_wallet_repository):
        """Should update balance on deposit."""
        wallet_id = uuid.uuid4()

        wallet = Wallet.create(
            user_id=uuid.uuid4(),
            address="0x1234567890abcdef1234567890abcdef12345678",
        )
        wallet.balance_usdt = 0.0

        mock_wallet_repository.get_by_id.return_value = wallet
        mock_wallet_repository.update.return_value = wallet

        updated = await wallet_service.update_balance(wallet_id, 100.0)

        assert updated is not None
        assert updated.balance_usdt == 100.0
        assert updated.total_received_usdt == 100.0
        assert updated.transaction_count == 1

    @pytest.mark.asyncio
    async def test_update_balance_returns_none_when_not_found(
        self, wallet_service, mock_wallet_repository
    ):
        """Should return None when wallet not found."""
        wallet_id = uuid.uuid4()
        mock_wallet_repository.get_by_id.return_value = None

        updated = await wallet_service.update_balance(wallet_id, 100.0)

        assert updated is None

    @pytest.mark.asyncio
    async def test_update_balance_withdrawal(self, wallet_service, mock_wallet_repository):
        """Should update balance on withdrawal."""
        wallet_id = uuid.uuid4()

        wallet = Wallet.create(
            user_id=uuid.uuid4(),
            address="0x1234567890abcdef1234567890abcdef12345678",
        )
        wallet.balance_usdt = 100.0

        mock_wallet_repository.get_by_id.return_value = wallet
        mock_wallet_repository.update.return_value = wallet

        updated = await wallet_service.update_balance(wallet_id, -50.0)

        assert updated is not None
        assert updated.balance_usdt == 50.0
