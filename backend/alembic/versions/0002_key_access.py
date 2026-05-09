"""key access

Revision ID: 0002_key_access
Revises: 0001_initial_schema
Create Date: 2026-05-09 00:00:01.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0002_key_access"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "key_access",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("can_encrypt", sa.Boolean(), nullable=False),
        sa.Column("can_decrypt", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["key_id"], ["kms_keys.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_id", "user_id", name="uq_key_access_user"),
    )
    op.create_index("ix_key_access_id", "key_access", ["id"])
    op.create_index("ix_key_access_key_id", "key_access", ["key_id"])
    op.create_index("ix_key_access_user_id", "key_access", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_key_access_user_id", table_name="key_access")
    op.drop_index("ix_key_access_key_id", table_name="key_access")
    op.drop_index("ix_key_access_id", table_name="key_access")
    op.drop_table("key_access")
