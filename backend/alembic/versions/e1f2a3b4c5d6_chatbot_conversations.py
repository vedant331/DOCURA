"""chatbot conversations and messages

Revision ID: e1f2a3b4c5d6
Revises: d4e5f6a7b8c9
Create Date: 2026-09-19 09:40:00.000000

The additive chatbot orchestration layer. Two tables:

* ``conversations`` — one authenticated user's chat thread, owned by exactly one account
  (``user_id`` ON DELETE CASCADE). Deleting a conversation removes only its messages; it
  never touches the user's documents, record, or sessions.
* ``conversation_messages`` — the ordered messages of a conversation. ``content`` is
  human-readable text; ``data`` (JSONB) carries value-free structured blocks (requirement
  statuses, readiness, actions). No third-party form content, no raw sensitive values.

Two native enums are declared at module level and dropped explicitly in ``downgrade``
(``op.drop_table`` leaves the PostgreSQL enum type behind), storing their values
("document_status"), matching the models and every other enum in the schema.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e1f2a3b4c5d6"
down_revision: str | Sequence[str] | None = "d4e5f6a7b8c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

message_role = sa.Enum("user", "assistant", "system", name="conversation_message_role")
message_type = sa.Enum(
    "text",
    "requirements",
    "document_status",
    "readiness",
    "question",
    "approval",
    "action",
    "error",
    name="conversation_message_type",
)


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_conversations_user_id_updated_at", "conversations", ["user_id", "updated_at"]
    )

    op.create_table(
        "conversation_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", message_role, nullable=False),
        sa.Column("message_type", message_type, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("data", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_conversation_messages_conversation_id_created_at",
        "conversation_messages",
        ["conversation_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_conversation_messages_conversation_id_created_at", table_name="conversation_messages"
    )
    op.drop_table("conversation_messages")
    op.drop_index("ix_conversations_user_id_updated_at", table_name="conversations")
    op.drop_table("conversations")
    message_type.drop(op.get_bind(), checkfirst=True)
    message_role.drop(op.get_bind(), checkfirst=True)
