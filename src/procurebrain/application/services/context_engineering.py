from dataclasses import dataclass

from procurebrain.application.services.retrieval_service import RetrievalService
from procurebrain.domain.chat.entities import ChatMessage
from procurebrain.memory.buffer import LangChainBufferMemoryService


@dataclass(slots=True)
class ContextBundle:
    conversation_buffer: str
    retrieved_context: str
    compressed_summary: str


class ContextEngineeringService:
    def __init__(
        self,
        buffer_memory: LangChainBufferMemoryService,
        retrieval_service: RetrievalService,
    ) -> None:
        self.buffer_memory = buffer_memory
        self.retrieval_service = retrieval_service

    def build_context_bundle(
        self,
        chat_id: str,
        query: str,
        history: list[ChatMessage],
        buffer_limit: int = 20,
        retrieval_limit: int = 5,
    ) -> ContextBundle:
        conversation_buffer = self.buffer_memory.build_transcript(history, max_messages=buffer_limit)
        chunks = self.retrieval_service.retrieve_for_chat(query=query, chat_id=chat_id, limit=retrieval_limit)
        retrieved_context = "\n\n".join(
            f"[{item.title}]\n{item.content}" for item in chunks
        ).strip()
        compressed_summary = self._compress(conversation_buffer, retrieved_context)
        return ContextBundle(
            conversation_buffer=conversation_buffer,
            retrieved_context=retrieved_context,
            compressed_summary=compressed_summary,
        )

    def _compress(self, conversation_buffer: str, retrieved_context: str, char_budget: int = 4000) -> str:
        combined = "\n\n".join(part for part in [conversation_buffer, retrieved_context] if part).strip()
        if len(combined) <= char_budget:
            return combined
        return combined[:char_budget].rsplit(" ", 1)[0] + "\n\n[Context truncated for budget]"
