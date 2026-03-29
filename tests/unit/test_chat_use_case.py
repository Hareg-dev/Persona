import asyncio
from datetime import datetime, timezone

from procurebrain.application.use_cases.send_message import SendMessageUseCase
from procurebrain.domain.chat.entities import ChatMessage, ChatSession
from procurebrain.domain.chat.schemas import SendMessageRequest
from procurebrain.domain.chat.service import ChatDomainService


class FakeChatRepository:
    async def get_by_id(self, chat_id: str):
        return ChatSession(id=chat_id, title="Test", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))

    async def touch(self, chat_id: str, updated_at):
        return None


class FakeMessageRepository:
    def __init__(self):
        self.messages = []

    async def create(self, message: ChatMessage):
        message.id = str(len(self.messages) + 1)
        self.messages.append(message)
        return message

    async def list_by_chat_id(self, chat_id: str):
        return self.messages


class FakeChatOrchestrator:
    async def generate_assistant_reply(self, **kwargs):
        return ("assistant reply", "openai", "gpt-4o-mini")


class FakeArtifactStore:
    def save_message(self, **kwargs):
        return None


def test_send_message_creates_user_and_assistant_messages():
    use_case = SendMessageUseCase(
        chat_repository=FakeChatRepository(),
        message_repository=FakeMessageRepository(),
        domain_service=ChatDomainService(),
        chat_orchestrator=FakeChatOrchestrator(),
        artifact_store=FakeArtifactStore(),
    )

    result = asyncio.run(use_case.execute("chat-1", SendMessageRequest(content="hello")))

    assert result.user_message.content == "hello"
    assert result.assistant_message is not None
    assert result.assistant_message.content == "assistant reply"
