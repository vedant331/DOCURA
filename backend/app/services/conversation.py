"""Conversation + message persistence for the chatbot layer.

Owner-scoped like every other DOCURA resource: identity comes from the session, and a
conversation is reached only through :func:`get_conversation`, which filters by ``user_id`` in
the ``WHERE`` clause (NFR-SEC-003). A guessed id belonging to another account is a 404, never a
disclosure. This module persists conversations and messages; it holds no product logic.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConversationNotFoundError
from app.db.models import (
    Conversation,
    ConversationMessage,
    ConversationMessageRole,
    ConversationMessageType,
)

DEFAULT_TITLE = "New conversation"
MESSAGE_PAGE_DEFAULT = 100
MESSAGE_PAGE_MAX = 500


async def create_conversation(
    db: AsyncSession, *, user_id: uuid.UUID, title: str | None = None
) -> Conversation:
    conversation = Conversation(
        user_id=user_id, title=(title or DEFAULT_TITLE).strip() or DEFAULT_TITLE
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def list_conversations(db: AsyncSession, *, user_id: uuid.UUID) -> list[Conversation]:
    """The caller's conversations, most-recently-active first."""
    result = await db.scalars(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
    )
    return list(result)


async def get_conversation(
    db: AsyncSession, *, user_id: uuid.UUID, conversation_id: uuid.UUID
) -> Conversation:
    """One conversation the caller owns, or :class:`ConversationNotFoundError`."""
    conversation = await db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id, Conversation.user_id == user_id
        )
    )
    if conversation is None:
        raise ConversationNotFoundError
    return conversation


async def rename_conversation(
    db: AsyncSession, *, user_id: uuid.UUID, conversation_id: uuid.UUID, title: str
) -> Conversation:
    conversation = await get_conversation(db, user_id=user_id, conversation_id=conversation_id)
    conversation.title = title.strip() or DEFAULT_TITLE
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def delete_conversation(
    db: AsyncSession, *, user_id: uuid.UUID, conversation_id: uuid.UUID
) -> None:
    """Delete one conversation and its messages (cascade). Never touches domain data."""
    conversation = await get_conversation(db, user_id=user_id, conversation_id=conversation_id)
    await db.execute(delete(Conversation).where(Conversation.id == conversation.id))
    await db.commit()


async def add_message(
    db: AsyncSession,
    *,
    conversation: Conversation,
    role: ConversationMessageRole,
    content: str,
    message_type: ConversationMessageType = ConversationMessageType.TEXT,
    data: dict[str, object] | None = None,
) -> ConversationMessage:
    """Append a message and mark the conversation active. Flushes (id/timestamps assigned);
    the caller owns the commit so a whole chat turn is one transaction."""
    # Set created_at explicitly (not the DB default): PostgreSQL's now() is the transaction
    # timestamp, so two messages appended in one turn would tie and their order would then
    # depend on random uuids. A Python timestamp per call keeps the user message before the
    # assistant reply deterministically.
    now = datetime.now(UTC)
    message = ConversationMessage(
        conversation_id=conversation.id,
        role=role,
        content=content,
        message_type=message_type,
        data=data,
        created_at=now,
    )
    db.add(message)
    # Touch the conversation so it rises to the top of the list on the next read.
    conversation.updated_at = now
    await db.flush()
    return message


async def list_messages(
    db: AsyncSession,
    *,
    conversation: Conversation,
    limit: int = MESSAGE_PAGE_DEFAULT,
    offset: int = 0,
) -> list[ConversationMessage]:
    """Messages in chronological order, paginated (defensive bounds)."""
    bounded = max(1, min(limit, MESSAGE_PAGE_MAX))
    result = await db.scalars(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation.id)
        .order_by(ConversationMessage.created_at, ConversationMessage.id)
        .limit(bounded)
        .offset(max(0, offset))
    )
    return list(result)
