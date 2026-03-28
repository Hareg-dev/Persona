from procurebrain.application.orchestrators.chat_orchestrator import ChatOrchestrator
from procurebrain.application.services.model_router import ModelRouter
from procurebrain.application.use_cases.create_chat import CreateChatUseCase
from procurebrain.application.use_cases.get_chat_history import GetChatHistoryUseCase
from procurebrain.application.use_cases.send_message import SendMessageUseCase
from procurebrain.domain.chat.service import ChatDomainService
from procurebrain.persistence.repositories.chat_repository import ChatRepository
from procurebrain.persistence.repositories.message_repository import MessageRepository
from procurebrain.skills.service import SkillService


def get_chat_repository() -> ChatRepository:
    return ChatRepository()


def get_message_repository() -> MessageRepository:
    return MessageRepository()


def get_chat_domain_service() -> ChatDomainService:
    return ChatDomainService()


def get_model_router() -> ModelRouter:
    return ModelRouter()


def get_skill_service() -> SkillService:
    return SkillService()


def get_chat_orchestrator() -> ChatOrchestrator:
    return ChatOrchestrator(
        model_router=get_model_router(),
        skill_service=get_skill_service(),
    )


def get_create_chat_use_case() -> CreateChatUseCase:
    return CreateChatUseCase(
        chat_repository=get_chat_repository(),
        domain_service=get_chat_domain_service(),
    )


def get_send_message_use_case() -> SendMessageUseCase:
    return SendMessageUseCase(
        chat_repository=get_chat_repository(),
        message_repository=get_message_repository(),
        domain_service=get_chat_domain_service(),
        chat_orchestrator=get_chat_orchestrator(),
    )


def get_chat_history_use_case() -> GetChatHistoryUseCase:
    return GetChatHistoryUseCase(
        chat_repository=get_chat_repository(),
        message_repository=get_message_repository(),
    )
