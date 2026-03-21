"""Tests unitarios para SubscriptionTransactionRepository."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from usipipo_commons.domain.entities.subscription_transaction import (
    SubscriptionTransaction,
    SubscriptionTransactionStatus,
)

from src.infrastructure.persistence.models.subscription_transaction_model import (
    SubscriptionTransactionModel,
)
from src.infrastructure.persistence.repositories.subscription_transaction_repository import (
    SubscriptionTransactionRepository,
)


@pytest.fixture
async def transaction_repo(test_session):
    """Crea una instancia de SubscriptionTransactionRepository."""
    return SubscriptionTransactionRepository(test_session)


@pytest.fixture
async def sample_transaction(test_session):
    """Crea una transacción de ejemplo en la base de datos."""
    now = datetime.now(UTC)
    transaction = SubscriptionTransaction(
        id=uuid.uuid4(),
        transaction_id="txn_test_123",
        user_id=123456,
        plan_type="one_month",
        amount_stars=360,
        payload='{"invoice_id": "inv_123"}',
        status=SubscriptionTransactionStatus.PENDING,
        created_at=now,
        expires_at=now + timedelta(minutes=30),
    )

    model = SubscriptionTransactionModel.from_entity(transaction)
    test_session.add(model)
    await test_session.commit()
    await test_session.refresh(model)

    return transaction


class TestSubscriptionTransactionRepositorySave:
    """Tests para el método save del repositorio."""

    @pytest.mark.asyncio
    async def test_save_creates_new_transaction(self, transaction_repo, test_session):
        """Verifica que save crea una nueva transacción."""
        now = datetime.now(UTC)
        transaction = SubscriptionTransaction(
            id=None,
            transaction_id="txn_new_456",
            user_id=789012,
            plan_type="three_months",
            amount_stars=960,
            payload='{"invoice_id": "inv_456"}',
            status=SubscriptionTransactionStatus.PENDING,
            created_at=now,
            expires_at=now + timedelta(minutes=30),
        )

        result = await transaction_repo.save(transaction)

        assert result is not None
        assert result.id is not None
        assert result.transaction_id == "txn_new_456"
        assert result.user_id == 789012
        assert result.plan_type == "three_months"
        assert result.amount_stars == 960
        assert result.status == SubscriptionTransactionStatus.PENDING

        # Verify in database
        db_result = await test_session.execute(
            select(SubscriptionTransactionModel).where(
                SubscriptionTransactionModel.transaction_id == "txn_new_456"
            )
        )
        db_model = db_result.scalar_one_or_none()
        assert db_model is not None
        assert db_model.user_id == 789012

    @pytest.mark.asyncio
    async def test_save_preserves_entity_data(self, transaction_repo, test_session):
        """Verifica que save preserva todos los datos de la entidad."""
        now = datetime.now(UTC)
        transaction = SubscriptionTransaction(
            id=uuid.uuid4(),
            transaction_id="txn_preserve_789",
            user_id=345678,
            plan_type="six_months",
            amount_stars=1560,
            payload='{"custom": "data", "number": 123}',
            status=SubscriptionTransactionStatus.PENDING,
            created_at=now,
            expires_at=now + timedelta(minutes=30),
        )

        result = await transaction_repo.save(transaction)

        assert result.transaction_id == transaction.transaction_id
        assert result.user_id == transaction.user_id
        assert result.plan_type == transaction.plan_type
        assert result.amount_stars == transaction.amount_stars
        assert result.payload == transaction.payload
        assert result.status == transaction.status


class TestSubscriptionTransactionRepositoryGetByTransactionId:
    """Tests para el método get_by_transaction_id del repositorio."""

    @pytest.mark.asyncio
    async def test_get_by_transaction_id_returns_transaction(
        self, transaction_repo, test_session, sample_transaction
    ):
        """Verifica que get_by_transaction_id retorna la transacción correcta."""
        result = await transaction_repo.get_by_transaction_id(sample_transaction.transaction_id)

        assert result is not None
        assert result.id == sample_transaction.id
        assert result.transaction_id == sample_transaction.transaction_id
        assert result.user_id == sample_transaction.user_id
        assert result.plan_type == sample_transaction.plan_type

    @pytest.mark.asyncio
    async def test_get_by_transaction_id_returns_none_for_nonexistent(
        self, transaction_repo, test_session
    ):
        """Verifica que get_by_transaction_id retorna None para ID inexistente."""
        result = await transaction_repo.get_by_transaction_id("txn_nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_transaction_id_converts_status_enum(
        self, transaction_repo, test_session, sample_transaction
    ):
        """Verifica que get_by_transaction_id convierte correctamente el status enum."""
        result = await transaction_repo.get_by_transaction_id(sample_transaction.transaction_id)

        assert result is not None
        assert isinstance(result.status, SubscriptionTransactionStatus)
        assert result.status == SubscriptionTransactionStatus.PENDING


class TestSubscriptionTransactionRepositoryGetByUser:
    """Tests para el método get_by_user del repositorio."""

    @pytest.mark.asyncio
    async def test_get_by_user_returns_transactions(self, transaction_repo, test_session):
        """Verifica que get_by_user retorna transacciones del usuario."""
        now = datetime.now(UTC)
        user_id = 111222

        # Create multiple transactions for the same user
        for i in range(5):
            transaction = SubscriptionTransaction(
                id=uuid.uuid4(),
                transaction_id=f"txn_user_test_{i}",
                user_id=user_id,
                plan_type="one_month",
                amount_stars=360,
                payload=f'{{"invoice_id": "inv_{i}"}}',
                status=SubscriptionTransactionStatus.PENDING,
                created_at=now - timedelta(minutes=i * 5),
                expires_at=now + timedelta(minutes=30),
            )
            model = SubscriptionTransactionModel.from_entity(transaction)
            test_session.add(model)
        await test_session.commit()

        result = await transaction_repo.get_by_user(user_id=user_id, limit=50)

        assert len(result) == 5
        assert all(t.user_id == user_id for t in result)

    @pytest.mark.asyncio
    async def test_get_by_user_respects_limit(self, transaction_repo, test_session):
        """Verifica que get_by_user respeta el límite."""
        now = datetime.now(UTC)
        user_id = 333444

        # Create 10 transactions for the user
        for i in range(10):
            transaction = SubscriptionTransaction(
                id=uuid.uuid4(),
                transaction_id=f"txn_limit_test_{i}",
                user_id=user_id,
                plan_type="one_month",
                amount_stars=360,
                payload=f'{{"invoice_id": "inv_{i}"}}',
                status=SubscriptionTransactionStatus.PENDING,
                created_at=now - timedelta(minutes=i),
                expires_at=now + timedelta(minutes=30),
            )
            model = SubscriptionTransactionModel.from_entity(transaction)
            test_session.add(model)
        await test_session.commit()

        result = await transaction_repo.get_by_user(user_id=user_id, limit=5)

        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_get_by_user_orders_by_created_at_desc(self, transaction_repo, test_session):
        """Verifica que get_by_user ordena por created_at descendente."""
        now = datetime.now(UTC)
        user_id = 555666

        # Create transactions with different timestamps
        transaction1 = SubscriptionTransaction(
            id=uuid.uuid4(),
            transaction_id="txn_order_1",
            user_id=user_id,
            plan_type="one_month",
            amount_stars=360,
            payload="{}",
            status=SubscriptionTransactionStatus.PENDING,
            created_at=now - timedelta(hours=2),
            expires_at=now + timedelta(minutes=30),
        )

        transaction2 = SubscriptionTransaction(
            id=uuid.uuid4(),
            transaction_id="txn_order_2",
            user_id=user_id,
            plan_type="one_month",
            amount_stars=360,
            payload="{}",
            status=SubscriptionTransactionStatus.PENDING,
            created_at=now - timedelta(hours=1),
            expires_at=now + timedelta(minutes=30),
        )

        transaction3 = SubscriptionTransaction(
            id=uuid.uuid4(),
            transaction_id="txn_order_3",
            user_id=user_id,
            plan_type="one_month",
            amount_stars=360,
            payload="{}",
            status=SubscriptionTransactionStatus.PENDING,
            created_at=now,
            expires_at=now + timedelta(minutes=30),
        )

        for t in [transaction1, transaction2, transaction3]:
            model = SubscriptionTransactionModel.from_entity(t)
            test_session.add(model)
        await test_session.commit()

        result = await transaction_repo.get_by_user(user_id=user_id, limit=50)

        assert len(result) == 3
        # Most recent should be first
        assert result[0].transaction_id == "txn_order_3"
        assert result[1].transaction_id == "txn_order_2"
        assert result[2].transaction_id == "txn_order_1"

    @pytest.mark.asyncio
    async def test_get_by_user_returns_empty_for_no_transactions(
        self, transaction_repo, test_session
    ):
        """Verifica que get_by_user retorna lista vacía sin transacciones."""
        result = await transaction_repo.get_by_user(user_id=999888, limit=50)

        assert len(result) == 0


class TestSubscriptionTransactionRepositoryMarkCompleted:
    """Tests para el método mark_completed del repositorio."""

    @pytest.mark.asyncio
    async def test_mark_completed_returns_true_for_pending(
        self, transaction_repo, test_session, sample_transaction
    ):
        """Verifica que mark_completed retorna True para transacción pending."""
        result = await transaction_repo.mark_completed(sample_transaction.transaction_id)

        assert result is True

        # Verify in database
        db_result = await test_session.execute(
            select(SubscriptionTransactionModel).where(
                SubscriptionTransactionModel.transaction_id == sample_transaction.transaction_id
            )
        )
        db_model = db_result.scalar_one_or_none()
        assert db_model is not None
        assert db_model.status == "completed"
        assert db_model.completed_at is not None

    @pytest.mark.asyncio
    async def test_mark_completed_returns_false_for_nonexistent(
        self, transaction_repo, test_session
    ):
        """Verifica que mark_completed retorna False para transacción inexistente."""
        result = await transaction_repo.mark_completed("txn_nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_mark_completed_sets_completed_at(
        self, transaction_repo, test_session, sample_transaction
    ):
        """Verifica que mark_completed establece completed_at."""
        before_mark = datetime.now(UTC)

        result = await transaction_repo.mark_completed(sample_transaction.transaction_id)

        assert result is True

        # Verify completed_at is set
        db_result = await test_session.execute(
            select(SubscriptionTransactionModel).where(
                SubscriptionTransactionModel.transaction_id == sample_transaction.transaction_id
            )
        )
        db_model = db_result.scalar_one_or_none()
        assert db_model is not None
        assert db_model.completed_at is not None
        # Compare timestamps (handle timezone-aware vs naive)
        completed_at = db_model.completed_at
        if completed_at.tzinfo is None:
            completed_at = completed_at.replace(tzinfo=UTC)
        assert completed_at >= before_mark

    @pytest.mark.asyncio
    async def test_mark_completed_works_for_already_completed(self, transaction_repo, test_session):
        """Verifica que mark_completed funciona para transacción ya completada."""
        now = datetime.now(UTC)
        transaction = SubscriptionTransaction(
            id=uuid.uuid4(),
            transaction_id="txn_already_completed",
            user_id=777888,
            plan_type="one_month",
            amount_stars=360,
            payload="{}",
            status=SubscriptionTransactionStatus.COMPLETED,
            created_at=now - timedelta(hours=1),
            expires_at=now + timedelta(minutes=30),
            completed_at=now - timedelta(minutes=30),
        )

        model = SubscriptionTransactionModel.from_entity(transaction)
        test_session.add(model)
        await test_session.commit()

        result = await transaction_repo.mark_completed("txn_already_completed")

        assert result is True


class TestSubscriptionTransactionRepositoryCleanupExpired:
    """Tests para el método cleanup_expired del repositorio."""

    @pytest.mark.asyncio
    async def test_cleanup_expired_removes_expired_pending(self, transaction_repo, test_session):
        """Verifica que cleanup_expired elimina transacciones pending expiradas."""
        now = datetime.now(UTC)

        # Create expired pending transaction
        expired_transaction = SubscriptionTransaction(
            id=uuid.uuid4(),
            transaction_id="txn_expired_pending",
            user_id=888999,
            plan_type="one_month",
            amount_stars=360,
            payload="{}",
            status=SubscriptionTransactionStatus.PENDING,
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(minutes=30),  # Expired
        )

        model = SubscriptionTransactionModel.from_entity(expired_transaction)
        test_session.add(model)
        await test_session.commit()

        # Count before cleanup
        count_before = await test_session.execute(
            select(SubscriptionTransactionModel).where(
                SubscriptionTransactionModel.transaction_id == "txn_expired_pending"
            )
        )
        assert count_before.scalar_one_or_none() is not None

        # Cleanup
        deleted_count = await transaction_repo.cleanup_expired()

        assert deleted_count == 1

        # Verify deleted
        count_after = await test_session.execute(
            select(SubscriptionTransactionModel).where(
                SubscriptionTransactionModel.transaction_id == "txn_expired_pending"
            )
        )
        assert count_after.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_cleanup_expired_keeps_non_expired_pending(self, transaction_repo, test_session):
        """Verifica que cleanup_expired mantiene transacciones pending no expiradas."""
        now = datetime.now(UTC)

        # Create non-expired pending transaction
        valid_transaction = SubscriptionTransaction(
            id=uuid.uuid4(),
            transaction_id="txn_valid_pending",
            user_id=999000,
            plan_type="one_month",
            amount_stars=360,
            payload="{}",
            status=SubscriptionTransactionStatus.PENDING,
            created_at=now,
            expires_at=now + timedelta(minutes=30),  # Not expired
        )

        model = SubscriptionTransactionModel.from_entity(valid_transaction)
        test_session.add(model)
        await test_session.commit()

        # Cleanup
        deleted_count = await transaction_repo.cleanup_expired()

        # Should not delete valid transaction
        assert deleted_count == 0

        # Verify still exists
        db_result = await test_session.execute(
            select(SubscriptionTransactionModel).where(
                SubscriptionTransactionModel.transaction_id == "txn_valid_pending"
            )
        )
        db_model = db_result.scalar_one_or_none()
        assert db_model is not None

    @pytest.mark.asyncio
    async def test_cleanup_expired_keeps_completed_transactions(
        self, transaction_repo, test_session
    ):
        """Verifica que cleanup_expired mantiene transacciones completadas."""
        now = datetime.now(UTC)

        # Create completed transaction (even if expired)
        completed_transaction = SubscriptionTransaction(
            id=uuid.uuid4(),
            transaction_id="txn_completed_old",
            user_id=111000,
            plan_type="one_month",
            amount_stars=360,
            payload="{}",
            status=SubscriptionTransactionStatus.COMPLETED,
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(minutes=30),
            completed_at=now - timedelta(hours=1),
        )

        model = SubscriptionTransactionModel.from_entity(completed_transaction)
        test_session.add(model)
        await test_session.commit()

        # Cleanup
        deleted_count = await transaction_repo.cleanup_expired()

        # Should not delete completed transaction
        assert deleted_count == 0

        # Verify still exists
        db_result = await test_session.execute(
            select(SubscriptionTransactionModel).where(
                SubscriptionTransactionModel.transaction_id == "txn_completed_old"
            )
        )
        db_model = db_result.scalar_one_or_none()
        assert db_model is not None

    @pytest.mark.asyncio
    async def test_cleanup_expired_returns_correct_count(self, transaction_repo, test_session):
        """Verifica que cleanup_expired retorna el conteo correcto de eliminados."""
        now = datetime.now(UTC)

        # Create multiple expired pending transactions
        for i in range(3):
            transaction = SubscriptionTransaction(
                id=uuid.uuid4(),
                transaction_id=f"txn_cleanup_{i}",
                user_id=222000,
                plan_type="one_month",
                amount_stars=360,
                payload="{}",
                status=SubscriptionTransactionStatus.PENDING,
                created_at=now - timedelta(hours=2),
                expires_at=now - timedelta(minutes=30),
            )
            model = SubscriptionTransactionModel.from_entity(transaction)
            test_session.add(model)

        # Create one valid transaction
        valid_transaction = SubscriptionTransaction(
            id=uuid.uuid4(),
            transaction_id="txn_cleanup_valid",
            user_id=222000,
            plan_type="one_month",
            amount_stars=360,
            payload="{}",
            status=SubscriptionTransactionStatus.PENDING,
            created_at=now,
            expires_at=now + timedelta(minutes=30),
        )
        model = SubscriptionTransactionModel.from_entity(valid_transaction)
        test_session.add(model)

        await test_session.commit()

        # Cleanup
        deleted_count = await transaction_repo.cleanup_expired()

        assert deleted_count == 3

    @pytest.mark.asyncio
    async def test_cleanup_expired_returns_zero_when_no_expired(
        self, transaction_repo, test_session
    ):
        """Verifica que cleanup_expired retorna 0 cuando no hay expirados."""
        deleted_count = await transaction_repo.cleanup_expired()

        assert deleted_count == 0


class TestSubscriptionTransactionModelConversion:
    """Tests para la conversión de modelos SQLAlchemy."""

    @pytest.mark.asyncio
    async def test_from_entity_creates_model(self, test_session):
        """Verifica que from_entity crea un modelo correcto."""
        now = datetime.now(UTC)
        transaction = SubscriptionTransaction(
            id=uuid.uuid4(),
            transaction_id="txn_model_test",
            user_id=123456,
            plan_type="one_month",
            amount_stars=360,
            payload='{"test": "data"}',
            status=SubscriptionTransactionStatus.PENDING,
            created_at=now,
            expires_at=now + timedelta(minutes=30),
        )

        model = SubscriptionTransactionModel.from_entity(transaction)

        assert model.transaction_id == transaction.transaction_id
        assert model.user_id == transaction.user_id
        assert model.plan_type == transaction.plan_type
        assert model.amount_stars == transaction.amount_stars
        assert model.payload == transaction.payload
        assert model.status == transaction.status

    @pytest.mark.asyncio
    async def test_to_entity_creates_entity(self, test_session):
        """Verifica que to_entity crea una entidad correcta."""
        now = datetime.now(UTC)
        model = SubscriptionTransactionModel(
            id=uuid.uuid4(),
            transaction_id="txn_entity_test",
            user_id=789012,
            plan_type="three_months",
            amount_stars=960,
            payload='{"entity": "test"}',
            status="pending",
            created_at=now,
            expires_at=now + timedelta(minutes=30),
        )

        entity = model.to_entity()

        assert entity.transaction_id == model.transaction_id
        assert entity.user_id == model.user_id
        assert entity.plan_type == model.plan_type
        assert entity.amount_stars == model.amount_stars
        assert entity.payload == model.payload
        assert entity.status == SubscriptionTransactionStatus.PENDING

    @pytest.mark.asyncio
    async def test_roundtrip_conversion(self, test_session):
        """Verifica que la conversión ida y vuelta preserva los datos."""
        now = datetime.now(UTC)
        original = SubscriptionTransaction(
            id=uuid.uuid4(),
            transaction_id="txn_roundtrip",
            user_id=345678,
            plan_type="six_months",
            amount_stars=1560,
            payload='{"roundtrip": "test"}',
            status=SubscriptionTransactionStatus.PENDING,
            created_at=now,
            expires_at=now + timedelta(minutes=30),
        )

        # Entity -> Model -> Entity
        model = SubscriptionTransactionModel.from_entity(original)
        result = model.to_entity()

        assert result.transaction_id == original.transaction_id
        assert result.user_id == original.user_id
        assert result.plan_type == original.plan_type
        assert result.amount_stars == original.amount_stars
        assert result.payload == original.payload
        assert result.status == original.status
