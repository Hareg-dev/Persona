from procurebrain.domain.chat.schemas import ChatSessionResponse, CreateChatRequest
from procurebrain.domain.chat.service import ChatDomainService
from procurebrain.persistence.repositories.chat_repository import ChatRepository


class CreateChatUseCase:
    def __init__(
        self,
        chat_repository: ChatRepository,
        domain_service: ChatDomainService,
    ) -> None:
        self.chat_repository = chat_repository
        self.domain_service = domain_service

    async def execute(self, request: CreateChatRequest) -> ChatSessionResponse:
        chat = self.domain_service.create_session(title=request.title, user_id=request.user_id)
        saved = await self.chat_repository.create(chat)
        return ChatSessionResponse(
            id=saved.id or "",
            title=saved.title,
            user_id=saved.user_id,
            status=saved.status,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )
