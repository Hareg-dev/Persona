from fastapi import APIRouter, Depends, Query

from procurebrain.api.deps import (
    get_assistant_ask_use_case,
    get_chat_history_use_case,
    get_create_chat_use_case,
    get_list_chats_use_case,
    get_send_message_use_case,
)
from procurebrain.application.use_cases.assistant_ask import AssistantAskUseCase
from procurebrain.application.use_cases.create_chat import CreateChatUseCase
from procurebrain.application.use_cases.get_chat_history import GetChatHistoryUseCase
from procurebrain.application.use_cases.list_chats import ListChatsUseCase
from procurebrain.application.use_cases.send_message import SendMessageUseCase
from procurebrain.domain.chat.schemas import (
    AssistantAskRequest,
    AssistantAskResponse,
    ChatHistoryResponse,
    ChatListResponse,
    ChatSessionResponse,
    ChatTurnResponse,
    CreateChatRequest,
    SendMessageRequest,
)

router = APIRouter()


@router.post("", response_model=ChatSessionResponse, status_code=201)
async def create_chat(
    request: CreateChatRequest,
    use_case: CreateChatUseCase = Depends(get_create_chat_use_case),
) -> ChatSessionResponse:
    return await use_case.execute(request)


@router.get("", response_model=ChatListResponse)
async def list_chats(
    user_id: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    use_case: ListChatsUseCase = Depends(get_list_chats_use_case),
) -> ChatListResponse:
    return await use_case.execute(user_id=user_id, limit=limit)


@router.post("/ask", response_model=AssistantAskResponse, status_code=201)
async def assistant_ask(
    request: AssistantAskRequest,
    use_case: AssistantAskUseCase = Depends(get_assistant_ask_use_case),
) -> AssistantAskResponse:
    return await use_case.execute(request)


@router.get("/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    chat_id: str,
    use_case: GetChatHistoryUseCase = Depends(get_chat_history_use_case),
) -> ChatHistoryResponse:
    return await use_case.execute(chat_id)


@router.post("/{chat_id}/messages", response_model=ChatTurnResponse, status_code=201)
async def send_message(
    chat_id: str,
    request: SendMessageRequest,
    use_case: SendMessageUseCase = Depends(get_send_message_use_case),
) -> ChatTurnResponse:
    return await use_case.execute(chat_id, request)
