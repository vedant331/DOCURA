"""sprint 4 extraction results

Revision ID: b2c3d4e5f6a7
Revises: f1a2b3c4d5e6
Create Date: 2026-09-08 15:20:00.000000

Sprint 4, second coding milestone: persist the engine-neutral extraction result —
a run, its pages, the text blocks on each page, their source regions, and the run's
metadata. Success-only and additive: a failed attempt writes no run, and a reprocess
adds a new run rather than replacing an old one. No enum types are introduced.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: str | Sequence[str] | None = "f1a2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "extraction_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("engine", sa.String(length=100), nullable=False),
        sa.Column("engine_version", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_extraction_runs_document_id_created_at",
        "extraction_runs",
        ["document_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "extraction_run_metadata",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("run_id", sa.UUID(), nullable=False),
        sa.Column("key", sa.String(length=200), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["extraction_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_extraction_run_metadata_run_id_key_unique",
        "extraction_run_metadata",
        ["run_id", "key"],
        unique=True,
    )

    op.create_table(
        "extraction_pages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("run_id", sa.UUID(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["extraction_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_extraction_pages_run_id_number_unique",
        "extraction_pages",
        ["run_id", "number"],
        unique=True,
    )

    op.create_table(
        "extraction_blocks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("page_id", sa.UUID(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("region_x", sa.Float(), nullable=True),
        sa.Column("region_y", sa.Float(), nullable=True),
        sa.Column("region_width", sa.Float(), nullable=True),
        sa.Column("region_height", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["page_id"], ["extraction_pages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_extraction_blocks_page_id_sequence_unique",
        "extraction_blocks",
        ["page_id", "sequence"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_extraction_blocks_page_id_sequence_unique", table_name="extraction_blocks")
    op.drop_table("extraction_blocks")
    op.drop_index("ix_extraction_pages_run_id_number_unique", table_name="extraction_pages")
    op.drop_table("extraction_pages")
    op.drop_index(
        "ix_extraction_run_metadata_run_id_key_unique", table_name="extraction_run_metadata"
    )
    op.drop_table("extraction_run_metadata")
    op.drop_index("ix_extraction_runs_document_id_created_at", table_name="extraction_runs")
    op.drop_table("extraction_runs")
