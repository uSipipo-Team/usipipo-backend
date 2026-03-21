"""Tests unitarios para ConsumptionInvoiceRepository."""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.consumption_invoice import ConsumptionInvoice
from usipipo_commons.domain.enums.consumption_payment_method import ConsumptionPaymentMethod
from usipipo_commons.domain.enums.invoice_status import InvoiceStatus

from src.infrastructure.persistence.repositories.consumption_invoice_repository import (
    ConsumptionInvoiceRepository,
)


@pytest.fixture
def mock_session():
    """Crea un mock de la sesión de SQLAlchemy."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.get = AsyncMock()
    session.add = AsyncMock()
    session.delete = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.merge = AsyncMock()
    return session


@pytest.fixture
def sample_invoice():
    """Crea una factura de consumo de ejemplo."""
    return ConsumptionInvoice(
        billing_id=uuid.uuid4(),
        user_id=123456,
        amount_usd=Decimal("5.50"),
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        payment_method=ConsumptionPaymentMethod.CRYPTO,
        status=InvoiceStatus.PENDING,
    )


@pytest.fixture
def repository(mock_session):
    """Crea una instancia del repositorio con sesión mock."""
    return ConsumptionInvoiceRepository(mock_session)


class TestConsumptionInvoiceRepository:
    """Tests unitarios para ConsumptionInvoiceRepository."""

    @pytest.mark.asyncio
    async def test_save_creates_new_invoice(self, repository, mock_session, sample_invoice):
        """Prueba que save crea una nueva factura correctamente."""
        # Arrange
        mock_model = MagicMock()
        mock_model.to_entity.return_value = sample_invoice
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None

        # Mock para que after commit tenga el ID
        sample_invoice.id = uuid.uuid4()

        # Act
        result = await repository.save(sample_invoice, current_user_id=999)

        # Assert
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert result == sample_invoice

    @pytest.mark.asyncio
    async def test_get_by_id_returns_invoice(self, repository, mock_session, sample_invoice):
        """Prueba que get_by_id retorna la factura cuando existe."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock(to_entity=lambda: sample_invoice)
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_id(sample_invoice.id or uuid.uuid4(), current_user_id=999)

        # Assert
        assert result == sample_invoice
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Prueba que get_by_id retorna None cuando no existe la factura."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_id(uuid.uuid4(), current_user_id=999)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_returns_list(self, repository, mock_session, sample_invoice):
        """Prueba que get_by_user retorna lista de facturas."""
        # Arrange
        mock_model = MagicMock()
        mock_model.to_entity.return_value = sample_invoice
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_user(user_id=123456, current_user_id=999)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == sample_invoice

    @pytest.mark.asyncio
    async def test_get_pending_by_user_returns_invoice(
        self, repository, mock_session, sample_invoice
    ):
        """Prueba que get_pending_by_user retorna la factura pendiente."""
        # Arrange
        mock_model = MagicMock()
        mock_model.to_entity.return_value = sample_invoice
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_pending_by_user(user_id=123456, current_user_id=999)

        # Assert
        assert result == sample_invoice

    @pytest.mark.asyncio
    async def test_get_pending_by_user_returns_none(self, repository, mock_session):
        """Prueba que get_pending_by_user retorna None cuando no hay factura pendiente."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_pending_by_user(user_id=123456, current_user_id=999)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_status_returns_list(self, repository, mock_session, sample_invoice):
        """Prueba que get_by_status retorna lista de facturas filtradas."""
        # Arrange
        mock_model = MagicMock()
        mock_model.to_entity.return_value = sample_invoice
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_status(InvoiceStatus.PENDING, current_user_id=999)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_expired_pending_returns_list(self, repository, mock_session, sample_invoice):
        """Prueba que get_expired_pending retorna facturas expiradas pendientes."""
        # Arrange
        mock_model = MagicMock()
        mock_model.to_entity.return_value = sample_invoice
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_expired_pending(current_user_id=999)

        # Assert
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_mark_as_paid_success(self, repository, mock_session, sample_invoice):
        """Prueba que mark_as_paid marca la factura como pagada."""
        # Arrange
        mock_model = MagicMock()
        mock_model.status = InvoiceStatus.PENDING.value
        mock_session.get.return_value = mock_model

        # Act
        result = await repository.mark_as_paid(
            invoice_id=sample_invoice.id or uuid.uuid4(),
            transaction_hash="0xabc123",
            current_user_id=999,
        )

        # Assert
        assert result is True
        assert mock_model.status == InvoiceStatus.PAID.value
        assert mock_model.transaction_hash == "0xabc123"
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_as_paid_returns_false_when_not_found(self, repository, mock_session):
        """Prueba que mark_as_paid retorna False cuando no existe la factura."""
        # Arrange
        mock_session.get.return_value = None

        # Act
        result = await repository.mark_as_paid(
            invoice_id=uuid.uuid4(),
            transaction_hash="0xabc123",
            current_user_id=999,
        )

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_mark_as_paid_returns_false_when_not_pending(self, repository, mock_session):
        """Prueba que mark_as_paid retorna False cuando la factura no está pendiente."""
        # Arrange
        mock_model = MagicMock()
        mock_model.status = InvoiceStatus.PAID.value
        mock_session.get.return_value = mock_model

        # Act
        result = await repository.mark_as_paid(
            invoice_id=uuid.uuid4(),
            transaction_hash="0xabc123",
            current_user_id=999,
        )

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_mark_as_expired_success(self, repository, mock_session):
        """Prueba que mark_as_expired marca la factura como expirada."""
        # Arrange
        mock_model = MagicMock()
        mock_model.status = InvoiceStatus.PENDING.value
        mock_session.get.return_value = mock_model

        # Act
        result = await repository.mark_as_expired(
            invoice_id=uuid.uuid4(),
            current_user_id=999,
        )

        # Assert
        assert result is True
        assert mock_model.status == InvoiceStatus.EXPIRED.value

    @pytest.mark.asyncio
    async def test_mark_as_expired_returns_false_when_paid(self, repository, mock_session):
        """Prueba que mark_as_expired retorna False cuando la factura ya está pagada."""
        # Arrange
        mock_model = MagicMock()
        mock_model.status = InvoiceStatus.PAID.value
        mock_session.get.return_value = mock_model

        # Act
        result = await repository.mark_as_expired(
            invoice_id=uuid.uuid4(),
            current_user_id=999,
        )

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_update_status_success(self, repository, mock_session):
        """Prueba que update_status actualiza el estado correctamente."""
        # Arrange
        mock_model = MagicMock()
        mock_session.get.return_value = mock_model

        # Act
        result = await repository.update_status(
            invoice_id=uuid.uuid4(),
            status=InvoiceStatus.EXPIRED,
            current_user_id=999,
        )

        # Assert
        assert result is True
        assert mock_model.status == InvoiceStatus.EXPIRED.value

    @pytest.mark.asyncio
    async def test_update_status_returns_false_when_not_found(self, repository, mock_session):
        """Prueba que update_status retorna False cuando no existe la factura."""
        # Arrange
        mock_session.get.return_value = None

        # Act
        result = await repository.update_status(
            invoice_id=uuid.uuid4(),
            status=InvoiceStatus.EXPIRED,
            current_user_id=999,
        )

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_success(self, repository, mock_session):
        """Prueba que delete elimina la factura correctamente."""
        # Arrange
        mock_model = MagicMock()
        mock_session.get.return_value = mock_model

        # Act
        result = await repository.delete(
            invoice_id=uuid.uuid4(),
            current_user_id=999,
        )

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_returns_false_when_not_found(self, repository, mock_session):
        """Prueba que delete retorna False cuando no existe la factura."""
        # Arrange
        mock_session.get.return_value = None

        # Act
        result = await repository.delete(
            invoice_id=uuid.uuid4(),
            current_user_id=999,
        )

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_get_by_billing_returns_list(self, repository, mock_session, sample_invoice):
        """Prueba que get_by_billing retorna lista de facturas de un ciclo."""
        # Arrange
        mock_model = MagicMock()
        mock_model.to_entity.return_value = sample_invoice
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.get_by_billing(
            billing_id=sample_invoice.billing_id,
            current_user_id=999,
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
