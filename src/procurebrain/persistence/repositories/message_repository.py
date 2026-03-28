from bson import ObjectId

from procurebrain.domain.chat.entities import ChatMessage
from procurebrain.persistence.mongodb.client import get_database
from procurebrain.persistence.mongodb.collections import MESSAGES


class MessageRepository:
    def __init__(self) -> None:
        self.collection = get_database()[MESSAGES]

    async def create(self, message: ChatMessage) -> ChatMessage:
        payload = {
            "chat_id": message.chat_id,
            "role": message.role,
            "content": message.content,
            "provider": message.provider,
            "model": message.model,
            "created_at": message.created_at,
        }
        result = await self.collection.insert_one(payload)
        message.id = str(result.inserted_id)
        return message

    async def list_by_chat_id(self, chat_id: str) -> list[ChatMessage]:
        cursor = self.collection.find({"chat_id": chat_id}).sort("created_at", 1)
        documents = await cursor.to_list(length=500)
        return [
            ChatMessage(
                id=str(document["_id"]),
                chat_id=document["chat_id"],
                role=document["role"],
                content=document["content"],
                provider=document.get("provider"),
                model=document.get("model"),
                created_at=document["created_at"],
            )
            for document in documents
        ]
