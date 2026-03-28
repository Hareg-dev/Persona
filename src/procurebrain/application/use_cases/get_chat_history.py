from fastapi import HTTPException, status

from procurebrain.domain.chat.schemas import ChatHistoryResponse, ChatSessionResponse, MessageResponse
from procurebrain.persistence.repositories.chat_repository import ChatRepository
from procurebrain.persistence.repositories.message_repository import MessageRepository


class GetChatHistoryUseCase:
    def __init__(
        self,
        chat_repository: ChatRepository,
        message_repository: MessageRepository,
    ) -> None:
        self.chat_repository = chat_repository
        self.message_repository = message_repository

    async def execute(self, chat_id: str) -> ChatHistoryResponse:
        chat = await self.chat_repository.get_by_id(chat_id)
        if chat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session '{chat_id}' was not found.",
            )

        messages = await self.message_repository.list_by_chat_id(chat_id)
        return ChatHistoryResponse(
            chat=ChatSessionResponse(
                id=chat.id or "",
                title=chat.title,
                user_id=chat.user_id,
                status=chat.status,
                created_at=chat.created_at,
                updated_at=chat.updated_at,
            ),
            messages=[
                MessageResponse(
                    id=item.id or "",
                    chat_id=item.chat_id,
                    role=item.role,
                    content=item.content,
                    provider=item.provider,
                    model=item.model,
                    created_at=item.created_at,
                )
                for item in messages
            ],
        )
