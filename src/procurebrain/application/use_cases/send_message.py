from fastapi import HTTPException, status

from procurebrain.domain.chat.entities import utc_now
from procurebrain.domain.chat.schemas import MessageResponse, SendMessageRequest
from procurebrain.domain.chat.service import ChatDomainService
from procurebrain.persistence.repositories.chat_repository import ChatRepository
from procurebrain.persistence.repositories.message_repository import MessageRepository


class SendMessageUseCase:
    def __init__(
        self,
        chat_repository: ChatRepository,
        message_repository: MessageRepository,
        domain_service: ChatDomainService,
    ) -> None:
        self.chat_repository = chat_repository
        self.message_repository = message_repository
        self.domain_service = domain_service

    async def execute(self, chat_id: str, request: SendMessageRequest) -> MessageResponse:
        chat = await self.chat_repository.get_by_id(chat_id)
        if chat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session '{chat_id}' was not found.",
            )

        message = self.domain_service.create_message(
            chat_id=chat_id,
            content=request.content,
            role=request.role,
            provider=request.provider,
            model=request.model,
        )
        saved = await self.message_repository.create(message)
        await self.chat_repository.touch(chat_id, utc_now())

        return MessageResponse(
            id=saved.id or "",
            chat_id=saved.chat_id,
            role=saved.role,
            content=saved.content,
            provider=saved.provider,
            model=saved.model,
            created_at=saved.created_at,
        )
