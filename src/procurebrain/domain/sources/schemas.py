from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class IngestUrlRequest(BaseModel):
    url: HttpUrl
    chat_id: str | None = None


class IngestPdfRequest(BaseModel):
    file_path: str = Field(min_length=1)
    chat_id: str | None = None
    title: str | None = None


class SourceResponse(BaseModel):
    id: str
    source_type: str
    title: str
    uri: str | None = None
    chat_id: str | None = None
    created_at: datetime
    updated_at: datetime


class RetrievedChunkResponse(BaseModel):
    source_id: str
    title: str
    content: str
    score: float | None = None
    uri: str | None = None
