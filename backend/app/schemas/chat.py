"""Chatbot API schemas — conversations, messages, and the assistant turn.

Value-free by construction: a message carries human-readable ``content`` and an optional
``data`` object of structured, value-free blocks (statuses, references, actions) — never raw
third-party form content or sensitive values.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# A single user message is bounded so an oversized payload cannot be appended.
MESSAGE_MAX_LENGTH = 4000
TITLE_MAX_LENGTH = 200


class ConversationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, max_length=TITLE_MAX_LENGTH)


class ConversationRename(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=TITLE_MAX_LENGTH)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversations: list[ConversationResponse]
    count: int


class MessageCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str = Field(min_length=1, max_length=MESSAGE_MAX_LENGTH)


class MessageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    role: str
    message_type: str
    content: str
    data: dict[str, Any] | None = None
    created_at: datetime


class MessageListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    messages: list[MessageResponse]
    count: int


class ChatTurnResponse(BaseModel):
    """The result of sending a message: the persisted user message and DOCURA's reply.

    The assistant's structure (response type, task, requirement/readiness blocks, actions,
    whether user input is needed) lives on ``assistant_message.data`` so the API stays
    extensible without a new response shape per task.
    """

    model_config = ConfigDict(extra="forbid")

    user_message: MessageResponse
    assistant_message: MessageResponse
