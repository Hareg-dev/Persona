from fastapi import HTTPException, status

from procurebrain.domain.chat.entities import utc_now
from procurebrain.application.orchestrators.chat_orchestrator import ChatOrchestrator
from procurebrain.domain.chat.schemas import ChatTurnResponse, MessageResponse, SendMessageRequest
from procurebrain.domain.chat.service import ChatDomainService
from procurebrain.persistence.repositories.chat_repository import ChatRepository
from procurebrain.persistence.repositories.message_repository import MessageRepository


class SendMessageUseCase:
    def __init__(
        self,
        chat_repository: ChatRepository,
        message_repository: MessageRepository,
        domain_service: ChatDomainService,
        chat_orchestrator: ChatOrchestrator,
    ) -> None:
        self.chat_repository = chat_repository
        self.message_repository = message_repository
        self.domain_service = domain_service
        self.chat_orchestrator = chat_orchestrator

    async def execute(self, chat_id: str, request: SendMessageRequest) -> ChatTurnResponse:
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
        user_response = MessageResponse(
            id=saved.id or "",
            chat_id=saved.chat_id,
            role=saved.role,
            content=saved.content,
            provider=saved.provider,
            model=saved.model,
            created_at=saved.created_at,
        )
        assistant_response: MessageResponse | None = None

        if request.role == "user":
            history = await self.message_repository.list_by_chat_id(chat_id)
            reply_content, provider_name, model_name = await self.chat_orchestrator.generate_assistant_reply(
                history=history,
                query=request.content,
                provider=request.provider,
                model=request.model,
            )
            assistant_message = self.domain_service.create_message(
                chat_id=chat_id,
                content=reply_content,
                role="assistant",
                provider=provider_name,
                model=model_name,
            )
            saved_assistant = await self.message_repository.create(assistant_message)
            assistant_response = MessageResponse(
                id=saved_assistant.id or "",
                chat_id=saved_assistant.chat_id,
                role=saved_assistant.role,
                content=saved_assistant.content,
                provider=saved_assistant.provider,
                model=saved_assistant.model,
                created_at=saved_assistant.created_at,
            )

        await self.chat_repository.touch(chat_id, utc_now())
        return ChatTurnResponse(
            user_message=user_response,
            assistant_message=assistant_response,
        )
