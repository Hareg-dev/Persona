from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class SourceRecord:
    source_type: str
    title: str
    content: str
    uri: str | None = None
    chat_id: str | None = None
    metadata: dict | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    id: str | None = None
