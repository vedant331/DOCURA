"""m1 form session and audit

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-09-09 19:35:00.000000

M1 — the form-session and audit foundation for the future extension and form-action
pipeline. Two tables:

* ``form_sessions`` — one authenticated user's session on a form, with a lifecycle
  state (active → handed_back / stopped / expired) and a start/end time. No form URL
  or third-party content is stored (BR-017, FR-AUD-006); a session is its own id.
* ``form_actions`` — the append-only history of what DOCURA did (FR-AUD-001…006),
  referencing provenance by id (document, observation) and pointing back at an earlier
  action for a reversal/correction (FR-AUD-005, BR-015). No file bytes, storage key,
  checksum, or extracted value; no third-party form content.

The three native enums are declared at module level and dropped explicitly in
``downgrade`` — ``op.drop_table`` leaves a PostgreSQL enum type behind, which the
up/down/up test would collide on — and store their values ("hand_back"), not member
names, matching the models and every other enum in the schema.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: str | Sequence[str] | None = "c3d4e5f6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

form_session_state = sa.Enum(
    "active",
    "handed_back",
    "stopped",
    "expired",
    name="form_session_state",
)
form_action_type = sa.Enum(
    "hand_back",
    "stop",
    "fill",
    "select",
    "attach",
    "ask",
    "answer",
    "approval_request",
    "approval_decision",
    "override",
    name="form_action_type",
)
form_action_outcome = sa.Enum(
    "succeeded",
    "failed",
    "skipped",
    name="form_action_outcome",
)


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "form_sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("state", form_session_state, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_form_sessions_user_id_created_at",
        "form_sessions",
        ["user_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "form_actions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("action_type", form_action_type, nullable=False),
        sa.Column("outcome", form_action_outcome, nullable=False),
        sa.Column("field_ref", sa.String(length=200), nullable=True),
        sa.Column("source_document_id", sa.UUID(), nullable=True),
        sa.Column("source_observation_id", sa.UUID(), nullable=True),
        sa.Column("reverses_action_id", sa.UUID(), nullable=True),
        sa.Column("detail", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["session_id"], ["form_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["source_observation_id"], ["attribute_observations.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["reverses_action_id"], ["form_actions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_form_actions_session_id_created_at",
        "form_actions",
        ["session_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_form_actions_session_id_created_at", table_name="form_actions")
    op.drop_table("form_actions")
    op.drop_index("ix_form_sessions_user_id_created_at", table_name="form_sessions")
    op.drop_table("form_sessions")
    form_action_outcome.drop(op.get_bind(), checkfirst=True)
    form_action_type.drop(op.get_bind(), checkfirst=True)
    form_session_state.drop(op.get_bind(), checkfirst=True)
