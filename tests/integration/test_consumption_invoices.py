"""Integration tests for consumption invoice endpoints."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from usipipo_commons.domain.entities.consumption_invoice import ConsumptionInvoice
from usipipo_commons.domain.enums.consumption_payment_method import ConsumptionPaymentMethod
from usipipo_commons.domain.enums.invoice_status import InvoiceStatus

from src.infrastructure.persistence.repositories.consumption_invoice_repository import (
    ConsumptionInvoiceRepository,
)


@pytest.mark.asyncio
async def test_create_invoice_requires_auth(client: AsyncClient):
    """Test that creating an invoice requires authentication."""
    response = await client.post("/api/v1/invoices", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_consumption_invoice(client: AsyncClient, auth_headers: dict):
    """Test creating a consumption invoice."""
    billing_id = str(uuid.uuid4())
    payload = {
        "billing_id": billing_id,
        "user_id": 123456,
        "amount_usd": "5.50",
        "payment_method": "crypto",
    }

    response = await client.post("/api/v1/invoices", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["billing_id"] == billing_id
    assert data["user_id"] == 123456
    assert data["amount_usd"] == "5.50"
    assert data["payment_method"] == "crypto"
    assert data["status"] == "pending"
    assert "id" in data
    assert "wallet_address" in data
    assert "expires_at" in data


@pytest.mark.asyncio
async def test_create_invoice_invalid_payment_method(client: AsyncClient, auth_headers: dict):
    """Test creating an invoice with invalid payment method."""
    payload = {
        "billing_id": str(uuid.uuid4()),
        "user_id": 123456,
        "amount_usd": "5.50",
        "payment_method": "invalid",
    }

    response = await client.post("/api/v1/invoices", json=payload, headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_invoice_by_id(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test getting an invoice by ID."""
    # Create test invoice
    invoice = ConsumptionInvoice(
        billing_id=uuid.uuid4(),
        user_id=123456,
        amount_usd=Decimal("10.00"),
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        payment_method=ConsumptionPaymentMethod.CRYPTO,
        status=InvoiceStatus.PENDING,
    )

    repo = ConsumptionInvoiceRepository(test_session)
    saved_invoice = await repo.save(invoice, 123456)

    response = await client.get(
        f"/api/v1/invoices/{saved_invoice.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(saved_invoice.id)
    assert data["amount_usd"] == "10.00"


@pytest.mark.asyncio
async def test_get_invoice_not_found(client: AsyncClient, auth_headers: dict):
    """Test getting a non-existent invoice."""
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/invoices/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_invoices(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test getting all invoices for a user."""
    # Create test invoices
    billing_id = uuid.uuid4()
    for i in range(3):
        invoice = ConsumptionInvoice(
            billing_id=billing_id,
            user_id=123456,
            amount_usd=Decimal(f"{5 + i}.00"),
            wallet_address=f"0x1234567890abcdef1234567890abcdef1234567{i}",
            payment_method=ConsumptionPaymentMethod.CRYPTO,
            status=InvoiceStatus.PENDING,
        )
        repo = ConsumptionInvoiceRepository(test_session)
        await repo.save(invoice, 123456)

    response = await client.get("/api/v1/invoices/user/123456", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "invoices" in data
    assert "total" in data
    assert data["total"] == 3
    assert "pending_count" in data
    assert "paid_count" in data
    assert "expired_count" in data


@pytest.mark.asyncio
async def test_get_user_pending_invoice(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test getting pending invoice for a user."""
    # Create test invoice
    invoice = ConsumptionInvoice(
        billing_id=uuid.uuid4(),
        user_id=123456,
        amount_usd=Decimal("7.50"),
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        payment_method=ConsumptionPaymentMethod.CRYPTO,
        status=InvoiceStatus.PENDING,
    )

    repo = ConsumptionInvoiceRepository(test_session)
    saved_invoice = await repo.save(invoice, 123456)

    response = await client.get("/api/v1/invoices/user/123456/pending", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(saved_invoice.id)
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_get_user_pending_invoice_none(client: AsyncClient, auth_headers: dict):
    """Test getting pending invoice when none exists."""
    response = await client.get("/api/v1/invoices/user/999999/pending", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.asyncio
async def test_get_billing_cycle_invoices(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test getting invoices for a billing cycle."""
    billing_id = uuid.uuid4()

    # Create test invoices
    for i in range(2):
        invoice = ConsumptionInvoice(
            billing_id=billing_id,
            user_id=123456,
            amount_usd=Decimal(f"{3 + i}.00"),
            wallet_address=f"0xabcdef1234567890abcdef1234567890abcdef1{i}",
            payment_method=ConsumptionPaymentMethod.CRYPTO,
            status=InvoiceStatus.PENDING,
        )
        repo = ConsumptionInvoiceRepository(test_session)
        await repo.save(invoice, 123456)

    response = await client.get(f"/api/v1/invoices/billing/{billing_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_mark_invoice_as_paid(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test marking an invoice as paid."""
    # Create test invoice
    invoice = ConsumptionInvoice(
        billing_id=uuid.uuid4(),
        user_id=123456,
        amount_usd=Decimal("15.00"),
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        payment_method=ConsumptionPaymentMethod.CRYPTO,
        status=InvoiceStatus.PENDING,
    )

    repo = ConsumptionInvoiceRepository(test_session)
    saved_invoice = await repo.save(invoice, 123456)

    payload = {"transaction_hash": "0xabc123def456"}
    response = await client.post(
        f"/api/v1/invoices/{saved_invoice.id}/pay",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "paid"
    assert data["transaction_hash"] == "0xabc123def456"


@pytest.mark.asyncio
async def test_mark_invoice_as_paid_not_pending(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test marking a non-pending invoice as paid."""
    # Create already paid invoice
    invoice = ConsumptionInvoice(
        billing_id=uuid.uuid4(),
        user_id=123456,
        amount_usd=Decimal("15.00"),
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        payment_method=ConsumptionPaymentMethod.CRYPTO,
        status=InvoiceStatus.PAID,
    )

    repo = ConsumptionInvoiceRepository(test_session)
    saved_invoice = await repo.save(invoice, 123456)

    payload = {"transaction_hash": "0xabc123"}
    response = await client.post(
        f"/api/v1/invoices/{saved_invoice.id}/pay",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_mark_invoice_as_expired(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test marking an invoice as expired."""
    # Create test invoice
    invoice = ConsumptionInvoice(
        billing_id=uuid.uuid4(),
        user_id=123456,
        amount_usd=Decimal("8.00"),
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        payment_method=ConsumptionPaymentMethod.CRYPTO,
        status=InvoiceStatus.PENDING,
    )

    repo = ConsumptionInvoiceRepository(test_session)
    saved_invoice = await repo.save(invoice, 123456)

    response = await client.post(
        f"/api/v1/invoices/{saved_invoice.id}/expire",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "expired"


@pytest.mark.asyncio
async def test_mark_invoice_as_expired_already_paid(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test marking a paid invoice as expired."""
    # Create already paid invoice
    invoice = ConsumptionInvoice(
        billing_id=uuid.uuid4(),
        user_id=123456,
        amount_usd=Decimal("8.00"),
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        payment_method=ConsumptionPaymentMethod.CRYPTO,
        status=InvoiceStatus.PAID,
    )

    repo = ConsumptionInvoiceRepository(test_session)
    saved_invoice = await repo.save(invoice, 123456)

    response = await client.post(
        f"/api/v1/invoices/{saved_invoice.id}/expire",
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_invoice_status(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test updating invoice status."""
    # Create test invoice
    invoice = ConsumptionInvoice(
        billing_id=uuid.uuid4(),
        user_id=123456,
        amount_usd=Decimal("12.00"),
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        payment_method=ConsumptionPaymentMethod.CRYPTO,
        status=InvoiceStatus.PENDING,
    )

    repo = ConsumptionInvoiceRepository(test_session)
    saved_invoice = await repo.save(invoice, 123456)

    payload = {"status": "expired"}
    response = await client.post(
        f"/api/v1/invoices/{saved_invoice.id}/status",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "expired"


@pytest.mark.asyncio
async def test_update_invoice_status_invalid(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test updating invoice status with invalid status."""
    # Create test invoice
    invoice = ConsumptionInvoice(
        billing_id=uuid.uuid4(),
        user_id=123456,
        amount_usd=Decimal("12.00"),
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        payment_method=ConsumptionPaymentMethod.CRYPTO,
        status=InvoiceStatus.PENDING,
    )

    repo = ConsumptionInvoiceRepository(test_session)
    saved_invoice = await repo.save(invoice, 123456)

    payload = {"status": "invalid_status"}
    response = await client.post(
        f"/api/v1/invoices/{saved_invoice.id}/status",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_invoice(client: AsyncClient, auth_headers: dict, test_session: AsyncSession):
    """Test deleting an invoice."""
    # Create test invoice
    invoice = ConsumptionInvoice(
        billing_id=uuid.uuid4(),
        user_id=123456,
        amount_usd=Decimal("6.00"),
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        payment_method=ConsumptionPaymentMethod.CRYPTO,
        status=InvoiceStatus.PENDING,
    )

    repo = ConsumptionInvoiceRepository(test_session)
    saved_invoice = await repo.save(invoice, 123456)

    response = await client.delete(
        f"/api/v1/invoices/{saved_invoice.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204

    # Verify it's deleted
    get_response = await client.get(
        f"/api/v1/invoices/{saved_invoice.id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_invoices_by_status(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test getting invoices by status."""
    # Create test invoices with different statuses
    billing_id = uuid.uuid4()
    for status in [InvoiceStatus.PENDING, InvoiceStatus.PENDING, InvoiceStatus.PAID]:
        invoice = ConsumptionInvoice(
            billing_id=billing_id,
            user_id=123456,
            amount_usd=Decimal("5.00"),
            wallet_address=f"0x1234567890abcdef1234567890abcdef12345678{status.value}",
            payment_method=ConsumptionPaymentMethod.CRYPTO,
            status=status,
        )
        repo = ConsumptionInvoiceRepository(test_session)
        await repo.save(invoice, 123456)

    response = await client.get("/api/v1/invoices/status/pending", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    for inv in data:
        assert inv["status"] == "pending"


@pytest.mark.asyncio
async def test_get_invoices_by_status_invalid(client: AsyncClient, auth_headers: dict):
    """Test getting invoices with invalid status."""
    response = await client.get("/api/v1/invoices/status/invalid", headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_expired_pending_invoices(
    client: AsyncClient, auth_headers: dict, test_session: AsyncSession
):
    """Test getting expired pending invoices."""
    # Create test invoice that's expired
    invoice = ConsumptionInvoice(
        billing_id=uuid.uuid4(),
        user_id=123456,
        amount_usd=Decimal("9.00"),
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
        payment_method=ConsumptionPaymentMethod.CRYPTO,
        status=InvoiceStatus.PENDING,
        expires_at=datetime.now(UTC) - timedelta(minutes=60),  # Expired 1 hour ago
    )

    repo = ConsumptionInvoiceRepository(test_session)
    await repo.save(invoice, 123456)

    response = await client.get("/api/v1/invoices/expired/pending", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Note: The invoice should be in the list since it's expired and pending
