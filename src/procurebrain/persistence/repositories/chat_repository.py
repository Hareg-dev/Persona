from bson import ObjectId

from procurebrain.domain.chat.entities import ChatSession
from procurebrain.persistence.mongodb.client import get_database
from procurebrain.persistence.mongodb.collections import CHAT_SESSIONS


class ChatRepository:
    def __init__(self) -> None:
        self.collection = get_database()[CHAT_SESSIONS]

    async def create(self, chat: ChatSession) -> ChatSession:
        payload = {
            "title": chat.title,
            "user_id": chat.user_id,
            "status": chat.status,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at,
        }
        result = await self.collection.insert_one(payload)
        chat.id = str(result.inserted_id)
        return chat

    async def get_by_id(self, chat_id: str) -> ChatSession | None:
        document = await self.collection.find_one({"_id": ObjectId(chat_id)})
        if document is None:
            return None
        return ChatSession(
            id=str(document["_id"]),
            title=document["title"],
            user_id=document.get("user_id"),
            status=document.get("status", "active"),
            created_at=document["created_at"],
            updated_at=document["updated_at"],
        )

    async def list_recent(self, user_id: str | None = None, limit: int = 20) -> list[ChatSession]:
        query = {"user_id": user_id} if user_id else {}
        cursor = self.collection.find(query).sort("updated_at", -1).limit(limit)
        documents = await cursor.to_list(length=limit)
        return [
            ChatSession(
                id=str(document["_id"]),
                title=document["title"],
                user_id=document.get("user_id"),
                status=document.get("status", "active"),
                created_at=document["created_at"],
                updated_at=document["updated_at"],
            )
            for document in documents
        ]

    async def get_latest_for_user(self, user_id: str | None = None) -> ChatSession | None:
        chats = await self.list_recent(user_id=user_id, limit=1)
        return chats[0] if chats else None

    async def touch(self, chat_id: str, updated_at) -> None:
        await self.collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"updated_at": updated_at}},
        )
