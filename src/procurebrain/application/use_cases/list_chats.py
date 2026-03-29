from procurebrain.domain.chat.schemas import ChatListResponse, ChatSessionResponse
from procurebrain.persistence.repositories.chat_repository import ChatRepository


class ListChatsUseCase:
    def __init__(self, chat_repository: ChatRepository) -> None:
        self.chat_repository = chat_repository

    async def execute(self, user_id: str | None = None, limit: int = 20) -> ChatListResponse:
        chats = await self.chat_repository.list_recent(user_id=user_id, limit=limit)
        return ChatListResponse(
            chats=[
                ChatSessionResponse(
                    id=item.id or "",
                    title=item.title,
                    user_id=item.user_id,
                    status=item.status,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
                for item in chats
            ]
        )
