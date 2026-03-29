from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from procurebrain.domain.intelligence.schemas import ResearchBriefResponse


class ChatIntent(str, Enum):
    QUERY = "query"
    RESEARCH = "research"
    NOTE = "note"


class ChatSelectionMode(str, Enum):
    AUTO_LATEST = "auto_latest"
    CREATE_NEW = "create_new"
    USE_EXISTING = "use_existing"


class ModelChoice(str, Enum):
    AUTO_BEST = "auto_best"
    OPENAI = "openai"
    GEMINI = "gemini"
    GROQ = "groq"


class ExportFormat(str, Enum):
    MARKDOWN = "markdown"
    PDF = "pdf"


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
    intent: ChatIntent = ChatIntent.QUERY
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


class ResolvedModelResponse(BaseModel):
    provider: str
    model: str


class ChatListResponse(BaseModel):
    chats: list[ChatSessionResponse]


class AssistantAskRequest(BaseModel):
    query: str = Field(min_length=1)
    user_id: str | None = None
    chat_mode: ChatSelectionMode = ChatSelectionMode.AUTO_LATEST
    chat_id: str | None = None
    chat_title: str | None = None
    intent: ChatIntent = ChatIntent.RESEARCH
    model_choice: ModelChoice = ModelChoice.AUTO_BEST
    model: str | None = None
    export_format: ExportFormat = ExportFormat.MARKDOWN
    include_audio: bool = False
    include_images: bool = True


class AssistantAskResponse(BaseModel):
    chat: ChatSessionResponse
    user_message: MessageResponse
    assistant_message: MessageResponse | None = None
    research: ResearchBriefResponse | None = None
    resolved_model: ResolvedModelResponse
