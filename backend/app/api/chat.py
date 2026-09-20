"""Chatbot API — conversations, messages, and the orchestrated assistant turn.

Every route is authenticated and owner-scoped (identity from the session, never a client id).
Sending a message runs the controlled orchestration layer and persists both the user message
and DOCURA's structured reply in one transaction. No route fills or submits a form.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from app.api.deps import AppSettings, CurrentUser, DbSession
from app.db.models import Conversation as ConversationModel
from app.db.models import ConversationMessage, ConversationMessageRole, ConversationMessageType
from app.schemas.chat import (
    ChatTurnResponse,
    ConversationCreate,
    ConversationListResponse,
    ConversationRename,
    ConversationResponse,
    MessageCreate,
    MessageListResponse,
    MessageResponse,
)
from app.services import conversation as conversations
from app.services.chatbot.orchestrator import build_orchestrator

router = APIRouter(prefix="/conversations", tags=["chat"])


def _to_conversation(row: ConversationModel) -> ConversationResponse:
    return ConversationResponse(
        id=row.id, title=row.title, created_at=row.created_at, updated_at=row.updated_at
    )


def _to_message(row: ConversationMessage) -> MessageResponse:
    return MessageResponse(
        id=row.id,
        role=row.role.value,
        message_type=row.message_type.value,
        content=row.content,
        data=row.data,
        created_at=row.created_at,
    )


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a conversation",
)
async def create_conversation(
    user: CurrentUser, db: DbSession, payload: ConversationCreate
) -> ConversationResponse:
    row = await conversations.create_conversation(db, user_id=user.id, title=payload.title)
    return _to_conversation(row)


@router.get("", response_model=ConversationListResponse, summary="List conversations")
async def list_conversations(user: CurrentUser, db: DbSession) -> ConversationListResponse:
    rows = await conversations.list_conversations(db, user_id=user.id)
    items = [_to_conversation(r) for r in rows]
    return ConversationListResponse(conversations=items, count=len(items))


@router.get(
    "/{conversation_id}", response_model=ConversationResponse, summary="Read a conversation"
)
async def read_conversation(
    conversation_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> ConversationResponse:
    row = await conversations.get_conversation(db, user_id=user.id, conversation_id=conversation_id)
    return _to_conversation(row)


@router.patch(
    "/{conversation_id}", response_model=ConversationResponse, summary="Rename a conversation"
)
async def rename_conversation(
    conversation_id: uuid.UUID, user: CurrentUser, db: DbSession, payload: ConversationRename
) -> ConversationResponse:
    row = await conversations.rename_conversation(
        db, user_id=user.id, conversation_id=conversation_id, title=payload.title
    )
    return _to_conversation(row)


@router.delete(
    "/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a conversation"
)
async def delete_conversation(conversation_id: uuid.UUID, user: CurrentUser, db: DbSession) -> None:
    await conversations.delete_conversation(db, user_id=user.id, conversation_id=conversation_id)


@router.post(
    "/{conversation_id}/messages",
    response_model=ChatTurnResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message",
)
async def send_message(
    conversation_id: uuid.UUID,
    user: CurrentUser,
    db: DbSession,
    settings: AppSettings,
    payload: MessageCreate,
) -> ChatTurnResponse:
    conversation = await conversations.get_conversation(
        db, user_id=user.id, conversation_id=conversation_id
    )
    # Prior turns for multi-turn context (owner-scoped: this conversation belongs to the caller).
    # Bounded and text-only — never structured data or sensitive values.
    prior = await conversations.list_messages(db, conversation=conversation, limit=12, offset=0)
    history = [m.content for m in prior if m.content]
    user_message = await conversations.add_message(
        db,
        conversation=conversation,
        role=ConversationMessageRole.USER,
        content=payload.content,
        message_type=ConversationMessageType.TEXT,
    )
    turn = await build_orchestrator(settings).handle(
        db, user_id=user.id, message=payload.content, history=history
    )
    assistant_message = await conversations.add_message(
        db,
        conversation=conversation,
        role=ConversationMessageRole.ASSISTANT,
        content=turn.message,
        message_type=turn.message_type,
        data=turn.data,
    )
    await db.commit()
    await db.refresh(user_message)
    await db.refresh(assistant_message)
    return ChatTurnResponse(
        user_message=_to_message(user_message),
        assistant_message=_to_message(assistant_message),
    )


@router.get(
    "/{conversation_id}/messages", response_model=MessageListResponse, summary="List messages"
)
async def list_messages(
    conversation_id: uuid.UUID,
    user: CurrentUser,
    db: DbSession,
    limit: int = 100,
    offset: int = 0,
) -> MessageListResponse:
    conversation = await conversations.get_conversation(
        db, user_id=user.id, conversation_id=conversation_id
    )
    rows = await conversations.list_messages(
        db, conversation=conversation, limit=limit, offset=offset
    )
    items = [_to_message(r) for r in rows]
    return MessageListResponse(messages=items, count=len(items))
