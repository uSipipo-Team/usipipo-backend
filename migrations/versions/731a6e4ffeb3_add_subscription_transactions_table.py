"""Add subscription_transactions table

Revision ID: 731a6e4ffeb3
Revises: 001_consolidated_schema
Create Date: 2026-03-18 06:17:28.690276

This migration adds the subscription_transactions table for tracking
Telegram Stars subscription payments and ensuring idempotency.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "731a6e4ffeb3"
down_revision: str | Sequence[str] | None = "001_consolidated_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create subscription_transactions table."""
    # Create subscription_transactions table
    op.create_table(
        "subscription_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("plan_type", sa.String(length=50), nullable=False),
        sa.Column("amount_stars", sa.Integer(), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "completed",
                "expired",
                "failed",
                name="subscription_transaction_status",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.telegram_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    # Create indexes
    op.create_index(
        op.f("ix_subscription_transactions_transaction_id"),
        "subscription_transactions",
        ["transaction_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_subscription_transactions_user_id"),
        "subscription_transactions",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop subscription_transactions table."""
    op.drop_index(
        op.f("ix_subscription_transactions_user_id"),
        table_name="subscription_transactions",
    )
    op.drop_index(
        op.f("ix_subscription_transactions_transaction_id"),
        table_name="subscription_transactions",
    )
    op.drop_table("subscription_transactions")
    # Drop enum type
    op.execute("DROP TYPE subscription_transaction_status")
