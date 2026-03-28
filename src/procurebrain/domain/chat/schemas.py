from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CreateChatRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    user_id: str | None = None


class ChatSessionResponse(BaseModel):
    id: str
    title: str
    user_id: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1)
    role: Literal["user", "assistant", "system"] = "user"
    provider: str | None = None
    model: str | None = None


class MessageResponse(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    provider: str | None = None
    model: str | None = None
    created_at: datetime


class ChatTurnResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse | None = None


class ChatHistoryResponse(BaseModel):
    chat: ChatSessionResponse
    messages: list[MessageResponse]
