from bson import ObjectId

from procurebrain.domain.sources.entities import SourceRecord
from procurebrain.persistence.mongodb.client import get_database
from procurebrain.persistence.mongodb.collections import SOURCES


class SourceRepository:
    def __init__(self) -> None:
        self.collection = get_database()[SOURCES]

    async def create(self, source: SourceRecord) -> SourceRecord:
        payload = {
            "source_type": source.source_type,
            "title": source.title,
            "content": source.content,
            "uri": source.uri,
            "chat_id": source.chat_id,
            "metadata": source.metadata or {},
            "created_at": source.created_at,
            "updated_at": source.updated_at,
        }
        result = await self.collection.insert_one(payload)
        source.id = str(result.inserted_id)
        return source

    async def get_by_id(self, source_id: str) -> SourceRecord | None:
        document = await self.collection.find_one({"_id": ObjectId(source_id)})
        if document is None:
            return None
        return SourceRecord(
            id=str(document["_id"]),
            source_type=document["source_type"],
            title=document["title"],
            content=document["content"],
            uri=document.get("uri"),
            chat_id=document.get("chat_id"),
            metadata=document.get("metadata", {}),
            created_at=document["created_at"],
            updated_at=document["updated_at"],
        )
