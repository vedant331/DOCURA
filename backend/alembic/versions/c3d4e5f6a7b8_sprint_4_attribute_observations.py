"""sprint 4 attribute observations

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-08 19:45:00.000000

Sprint 4, third coding milestone: the structured attribute observation layer. One
table, ``attribute_observations`` — a value recognised as a canonical attribute (by
its vocabulary identifier only), the block it was read from (exact provenance), and
the confidence it was read with. Owned by the producing run, so a reprocess adds new
observations without disturbing an earlier run's, and "current" is the newest run's
with no stored flag. No enum types, no field/attribute/sensitivity definition, and no
file metadata are introduced.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: str | Sequence[str] | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "attribute_observations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("run_id", sa.UUID(), nullable=False),
        sa.Column("source_block_id", sa.UUID(), nullable=False),
        sa.Column("canonical_identifier", sa.String(length=200), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["run_id"], ["extraction_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["source_block_id"], ["extraction_blocks.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_attribute_observations_run_id",
        "attribute_observations",
        ["run_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_attribute_observations_run_id", table_name="attribute_observations")
    op.drop_table("attribute_observations")
