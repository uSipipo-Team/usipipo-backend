"""Tests unitarios para SubscriptionPaymentService."""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from usipipo_commons.domain.entities.subscription_plan import (
    PlanType,
    SubscriptionPlan,
)

from src.core.application.services.subscription_payment_service import (
    SubscriptionPaymentService,
)
from src.core.application.services.subscription_service import SubscriptionService
from src.infrastructure.payment_gateways.telegram_stars_client import TelegramStarsClient


@pytest.fixture
def mock_subscription_service():
    """Crea un mock del servicio de suscripciones."""
    service = AsyncMock(spec=SubscriptionService)
    service.get_plan_option = MagicMock()
    service.is_premium_user = AsyncMock()
    service.activate_subscription = AsyncMock()
    return service


@pytest.fixture
def mock_crypto_payment_service():
    """Crea un mock del servicio de pagos crypto."""
    service = AsyncMock()
    service.create_order = AsyncMock()
    return service


@pytest.fixture
def mock_telegram_stars_client():
    """Crea un mock del cliente de Telegram Stars."""
    client = AsyncMock(spec=TelegramStarsClient)
    client.create_invoice = AsyncMock()
    return client


@pytest.fixture
def subscription_payment_service(
    mock_subscription_service,
    mock_crypto_payment_service,
    mock_telegram_stars_client,
):
    """Crea una instancia de SubscriptionPaymentService con dependencias mock."""
    return SubscriptionPaymentService(
        subscription_service=mock_subscription_service,
        crypto_payment_service=mock_crypto_payment_service,
        telegram_stars_client=mock_telegram_stars_client,
    )


@pytest.fixture
def sample_plan_option():
    """Crea una opción de plan de ejemplo."""
    from src.core.application.services.subscription_service import SubscriptionOption

    return SubscriptionOption(
        name="1 Month",
        plan_type=PlanType.ONE_MONTH,
        duration_months=1,
        stars=360,
        usdt=2.99,
    )


@pytest.fixture
def sample_subscription_plan():
    """Crea un plan de suscripción de ejemplo."""
    now = datetime.now(UTC)
    return SubscriptionPlan(
        id=uuid.uuid4(),
        user_id=123456,
        plan_type=PlanType.ONE_MONTH,
        stars_paid=360,
        payment_id="payment_123",
        starts_at=now,
        expires_at=now + timedelta(days=30),
        is_active=True,
    )


class TestCreateStarsInvoice:
    """Tests para el método create_stars_invoice."""

    @pytest.mark.asyncio
    async def test_creates_invoice_successfully(
        self,
        subscription_payment_service,
        mock_subscription_service,
        mock_telegram_stars_client,
        sample_plan_option,
    ):
        """Verifica creación exitosa de factura Stars."""
        # Configurar mocks
        mock_subscription_service.get_plan_option.return_value = sample_plan_option
        mock_subscription_service.is_premium_user.return_value = False
        mock_telegram_stars_client.create_invoice.return_value = {
            "result": {"invoice_link": "https://t.me/invoice/123"}
        }

        # Ejecutar
        result = await subscription_payment_service.create_stars_invoice(
            user_id=123456,
            plan_type="one_month",
            transaction_id="txn_123",
        )

        # Verificar
        assert result["success"] is True
        assert result["transaction_id"] == "txn_123"
        assert result["amount_stars"] == 360
        assert "payload" in result
        assert result["payload"] == "subscription_one_month_123456_txn_123"
        assert result["invoice_link"] == {"invoice_link": "https://t.me/invoice/123"}

        # Verificar llamadas
        mock_subscription_service.get_plan_option.assert_called_once_with("one_month")
        mock_subscription_service.is_premium_user.assert_called_once_with(123456, 123456)
        mock_telegram_stars_client.create_invoice.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_error_for_invalid_plan(
        self,
        subscription_payment_service,
        mock_subscription_service,
    ):
        """Verifica que lanza error para plan inválido."""
        mock_subscription_service.get_plan_option.return_value = None

        with pytest.raises(ValueError, match="Plan no válido"):
            await subscription_payment_service.create_stars_invoice(
                user_id=123456,
                plan_type="invalid_plan",
                transaction_id="txn_123",
            )

    @pytest.mark.asyncio
    async def test_raises_error_for_existing_subscription(
        self,
        subscription_payment_service,
        mock_subscription_service,
        sample_plan_option,
    ):
        """Verifica que lanza error si ya existe suscripción."""
        mock_subscription_service.get_plan_option.return_value = sample_plan_option
        mock_subscription_service.is_premium_user.return_value = True

        with pytest.raises(ValueError, match="Ya tienes una suscripción activa"):
            await subscription_payment_service.create_stars_invoice(
                user_id=123456,
                plan_type="one_month",
                transaction_id="txn_123",
            )

    @pytest.mark.asyncio
    async def test_raises_error_when_invoice_creation_fails(
        self,
        subscription_payment_service,
        mock_subscription_service,
        mock_telegram_stars_client,
        sample_plan_option,
    ):
        """Verifica que lanza error cuando falla creación de factura."""
        mock_subscription_service.get_plan_option.return_value = sample_plan_option
        mock_subscription_service.is_premium_user.return_value = False
        # Simular excepción en el cliente
        mock_telegram_stars_client.create_invoice.side_effect = Exception("Invoice creation failed")

        with pytest.raises(Exception, match="No se pudo crear la factura"):
            await subscription_payment_service.create_stars_invoice(
                user_id=123456,
                plan_type="one_month",
                transaction_id="txn_123",
            )

    @pytest.mark.asyncio
    async def test_invoice_payload_format(
        self,
        subscription_payment_service,
        mock_subscription_service,
        mock_telegram_stars_client,
        sample_plan_option,
    ):
        """Verifica formato correcto del payload."""
        mock_subscription_service.get_plan_option.return_value = sample_plan_option
        mock_subscription_service.is_premium_user.return_value = False
        mock_telegram_stars_client.create_invoice.return_value = {"result": {}}

        result = await subscription_payment_service.create_stars_invoice(
            user_id=999888,
            plan_type="three_months",
            transaction_id="txn_abc",
        )

        assert result["payload"] == "subscription_three_months_999888_txn_abc"


class TestCreateCryptoOrder:
    """Tests para el método create_crypto_order."""

    @pytest.mark.asyncio
    async def test_creates_order_successfully(
        self,
        subscription_payment_service,
        mock_subscription_service,
        sample_plan_option,
    ):
        """Verifica creación exitosa de orden crypto."""
        mock_subscription_service.get_plan_option.return_value = sample_plan_option
        mock_subscription_service.is_premium_user.return_value = False

        result = await subscription_payment_service.create_crypto_order(
            user_id=123456,
            plan_type="one_month",
            transaction_id="txn_123",
        )

        assert result["success"] is True
        assert result["transaction_id"] == "txn_123"
        assert result["plan_type"] == "one_month"
        assert result["amount_usdt"] == 2.99
        assert "wallet_address" in result
        assert "qr_code_url" in result
        assert result["qr_code_url"] == "/api/v1/crypto/qr/txn_123"

    @pytest.mark.asyncio
    async def test_raises_error_for_invalid_plan(
        self,
        subscription_payment_service,
        mock_subscription_service,
    ):
        """Verifica que lanza error para plan inválido."""
        mock_subscription_service.get_plan_option.return_value = None

        with pytest.raises(ValueError, match="Plan no válido"):
            await subscription_payment_service.create_crypto_order(
                user_id=123456,
                plan_type="invalid_plan",
                transaction_id="txn_123",
            )

    @pytest.mark.asyncio
    async def test_raises_error_for_existing_subscription(
        self,
        subscription_payment_service,
        mock_subscription_service,
        sample_plan_option,
    ):
        """Verifica que lanza error si ya existe suscripción."""
        mock_subscription_service.get_plan_option.return_value = sample_plan_option
        mock_subscription_service.is_premium_user.return_value = True

        with pytest.raises(ValueError, match="Ya tienes una suscripción activa"):
            await subscription_payment_service.create_crypto_order(
                user_id=123456,
                plan_type="one_month",
                transaction_id="txn_123",
            )

    @pytest.mark.asyncio
    async def test_different_plan_amounts(
        self,
        subscription_payment_service,
        mock_subscription_service,
    ):
        """Verifica diferentes montos para diferentes planes."""
        from src.core.application.services.subscription_service import SubscriptionOption

        plans = [
            ("one_month", 2.99),
            ("three_months", 7.99),
            ("six_months", 12.99),
        ]

        for plan_type, expected_amount in plans:
            plan_option = SubscriptionOption(
                name="Test",
                plan_type=PlanType(plan_type),
                duration_months=1,
                stars=100,
                usdt=expected_amount,
            )
            mock_subscription_service.get_plan_option.return_value = plan_option
            mock_subscription_service.is_premium_user.return_value = False

            result = await subscription_payment_service.create_crypto_order(
                user_id=123456,
                plan_type=plan_type,
                transaction_id=f"txn_{plan_type}",
            )

            assert result["amount_usdt"] == expected_amount


class TestHandleStarsPaymentSuccess:
    """Tests para el método handle_stars_payment_success."""

    @pytest.mark.asyncio
    async def test_activates_subscription_successfully(
        self,
        subscription_payment_service,
        mock_subscription_service,
        sample_plan_option,
        sample_subscription_plan,
    ):
        """Verifica activación exitosa tras pago Stars."""
        mock_subscription_service.get_plan_option.return_value = sample_plan_option
        mock_subscription_service.activate_subscription.return_value = sample_subscription_plan

        result = await subscription_payment_service.handle_stars_payment_success(
            user_id=123456,
            plan_type="one_month",
            transaction_id="txn_123",
            telegram_payment_id="tg_pay_123",
            current_user_id=999999,
        )

        assert result["success"] is True
        assert result["subscription_id"] == str(sample_subscription_plan.id)
        assert result["plan_type"] == "one_month"
        assert "expires_at" in result

        mock_subscription_service.activate_subscription.assert_called_once_with(
            user_id=123456,
            plan_type="one_month",
            stars_paid=360,
            payment_id="tg_pay_123",
            current_user_id=999999,
        )

    @pytest.mark.asyncio
    async def test_raises_error_for_invalid_plan(
        self,
        subscription_payment_service,
        mock_subscription_service,
    ):
        """Verifica que lanza error para plan inválido."""
        mock_subscription_service.get_plan_option.return_value = None

        with pytest.raises(ValueError, match="Plan no válido"):
            await subscription_payment_service.handle_stars_payment_success(
                user_id=123456,
                plan_type="invalid_plan",
                transaction_id="txn_123",
                telegram_payment_id="tg_pay_123",
                current_user_id=999999,
            )


class TestHandleCryptoPaymentSuccess:
    """Tests para el método handle_crypto_payment_success."""

    @pytest.mark.asyncio
    async def test_activates_subscription_successfully(
        self,
        subscription_payment_service,
        mock_subscription_service,
        sample_plan_option,
        sample_subscription_plan,
    ):
        """Verifica activación exitosa tras pago crypto."""
        mock_subscription_service.get_plan_option.return_value = sample_plan_option
        mock_subscription_service.activate_subscription.return_value = sample_subscription_plan

        result = await subscription_payment_service.handle_crypto_payment_success(
            user_id=123456,
            plan_type="one_month",
            transaction_id="txn_123",
            crypto_payment_id="crypto_pay_123",
            current_user_id=999999,
        )

        assert result["success"] is True
        assert result["subscription_id"] == str(sample_subscription_plan.id)
        assert result["plan_type"] == "one_month"
        assert "expires_at" in result

        mock_subscription_service.activate_subscription.assert_called_once_with(
            user_id=123456,
            plan_type="one_month",
            stars_paid=360,
            payment_id="crypto_pay_123",
            current_user_id=999999,
        )

    @pytest.mark.asyncio
    async def test_raises_error_for_invalid_plan(
        self,
        subscription_payment_service,
        mock_subscription_service,
    ):
        """Verifica que lanza error para plan inválido."""
        mock_subscription_service.get_plan_option.return_value = None

        with pytest.raises(ValueError, match="Plan no válido"):
            await subscription_payment_service.handle_crypto_payment_success(
                user_id=123456,
                plan_type="invalid_plan",
                transaction_id="txn_123",
                crypto_payment_id="crypto_pay_123",
                current_user_id=999999,
            )


class TestSubscriptionPaymentServiceInit:
    """Tests para la inicialización del servicio."""

    def test_init_with_all_dependencies(
        self,
        mock_subscription_service,
        mock_crypto_payment_service,
        mock_telegram_stars_client,
    ):
        """Verifica inicialización con todas las dependencias."""
        service = SubscriptionPaymentService(
            subscription_service=mock_subscription_service,
            crypto_payment_service=mock_crypto_payment_service,
            telegram_stars_client=mock_telegram_stars_client,
        )

        assert service.subscription_service == mock_subscription_service
        assert service.crypto_payment_service == mock_crypto_payment_service
        assert service.telegram_stars_client == mock_telegram_stars_client

    def test_init_with_optional_dependencies(
        self,
        mock_subscription_service,
    ):
        """Verifica inicialización con dependencias opcionales."""
        service = SubscriptionPaymentService(
            subscription_service=mock_subscription_service,
        )

        assert service.subscription_service == mock_subscription_service
        assert service.crypto_payment_service is None
        assert service.telegram_stars_client is not None
        assert isinstance(service.telegram_stars_client, TelegramStarsClient)


class TestIntegrationWithSubscriptionService:
    """Tests de integración con SubscriptionService."""

    @pytest.mark.asyncio
    async def test_uses_correct_stars_amount(
        self,
        subscription_payment_service,
        mock_subscription_service,
        mock_telegram_stars_client,
    ):
        """Verifica que usa la cantidad correcta de Stars."""
        from src.core.application.services.subscription_service import SubscriptionOption

        plan_option = SubscriptionOption(
            name="3 Months",
            plan_type=PlanType.THREE_MONTHS,
            duration_months=3,
            stars=960,
            usdt=7.99,
        )
        mock_subscription_service.get_plan_option.return_value = plan_option
        mock_subscription_service.is_premium_user.return_value = False
        mock_telegram_stars_client.create_invoice.return_value = {"result": {}}

        await subscription_payment_service.create_stars_invoice(
            user_id=123456,
            plan_type="three_months",
            transaction_id="txn_123",
        )

        # Verificar que se llamó con el USDT correcto (que se convierte a Stars internamente)
        call_args = mock_telegram_stars_client.create_invoice.call_args
        assert call_args[1]["amount_usd"] == 7.99
        assert call_args[1]["user_telegram_id"] == 123456

    @pytest.mark.asyncio
    async def test_uses_correct_usdt_amount_for_crypto(
        self,
        subscription_payment_service,
        mock_subscription_service,
    ):
        """Verifica que usa la cantidad correcta de USDT para crypto."""
        from src.core.application.services.subscription_service import SubscriptionOption

        plan_option = SubscriptionOption(
            name="6 Months",
            plan_type=PlanType.SIX_MONTHS,
            duration_months=6,
            stars=1560,
            usdt=12.99,
        )
        mock_subscription_service.get_plan_option.return_value = plan_option
        mock_subscription_service.is_premium_user.return_value = False

        result = await subscription_payment_service.create_crypto_order(
            user_id=123456,
            plan_type="six_months",
            transaction_id="txn_123",
        )

        assert result["amount_usdt"] == 12.99
