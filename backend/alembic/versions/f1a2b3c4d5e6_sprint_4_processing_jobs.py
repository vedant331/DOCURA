"""sprint 4 processing jobs

Revision ID: f1a2b3c4d5e6
Revises: b9e5ec480815
Create Date: 2026-09-08 14:40:00.000000

Sprint 4 decision D-09 (Option B): a durable job table that drives extraction, and
the one user-facing column that FR-OCR-009 needs on a document — a failure reason.

Adjusted in the same two places as the Sprint 3 migration:

* ``job_state`` is declared once at module level and dropped explicitly in
  ``downgrade`` — ``op.drop_table`` leaves a PostgreSQL enum type behind, which would
  make the next upgrade collide.
* The enum stores its values ("pending"), not member names ("PENDING"), matching the
  model and what any reader of the table sees.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: str | Sequence[str] | None = "b9e5ec480815"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

job_state = sa.Enum(
    "pending",
    "claimed",
    "succeeded",
    "failed",
    name="job_state",
)


def upgrade() -> None:
    """Upgrade schema."""
    # FR-OCR-009: a document that fails processing states what failed. User-facing
    # text, so it lives on the document rather than the internal job.
    op.add_column(
        "documents",
        sa.Column("failure_reason", sa.String(length=500), nullable=True),
    )

    op.create_table(
        "processing_jobs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("state", job_state, nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_processing_jobs_document_id_unique",
        "processing_jobs",
        ["document_id"],
        unique=True,
    )
    op.create_index(
        "ix_processing_jobs_state_created_at",
        "processing_jobs",
        ["state", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_processing_jobs_state_created_at", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_document_id_unique", table_name="processing_jobs")
    op.drop_table("processing_jobs")
    job_state.drop(op.get_bind(), checkfirst=True)
    op.drop_column("documents", "failure_reason")
