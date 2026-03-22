"""change vpn_keys user_id from integer to uuid

Revision ID: 6f80ea3bfca9
Revises: a3c6f868712d
Create Date: 2026-03-21 22:01:19.178301

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6f80ea3bfca9"
down_revision: str | Sequence[str] | None = "a3c6f868712d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop existing data (user_id values are telegram_ids, not UUIDs)
    op.execute("DELETE FROM vpn_keys")

    # Drop index on user_id
    op.drop_index("ix_vpn_keys_user_id", table_name="vpn_keys")

    # Drop the old column
    op.drop_column("vpn_keys", "user_id")

    # Add new column with UUID type
    op.add_column("vpn_keys", sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False))

    # Create index
    op.create_index("ix_vpn_keys_user_id", "vpn_keys", ["user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index
    op.drop_index("ix_vpn_keys_user_id", table_name="vpn_keys")

    # Drop the UUID column
    op.drop_column("vpn_keys", "user_id")

    # Add back the INTEGER column with index
    op.add_column("vpn_keys", sa.Column("user_id", sa.Integer(), nullable=False))
    op.create_index("ix_vpn_keys_user_id", "vpn_keys", ["user_id"])
