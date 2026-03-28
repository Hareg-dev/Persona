from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class ChatSession:
    title: str
    user_id: str | None = None
    status: str = "active"
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    id: str | None = None


@dataclass(slots=True)
class ChatMessage:
    chat_id: str
    role: str
    content: str
    provider: str | None = None
    model: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    id: str | None = None
