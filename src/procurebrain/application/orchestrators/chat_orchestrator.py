from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from procurebrain.application.services.model_router import ModelRouter
from procurebrain.application.services.retrieval_service import RetrievalService
from procurebrain.memory.buffer import LangChainBufferMemoryService
from procurebrain.domain.chat.entities import ChatMessage
from procurebrain.skills.service import SkillService


class ChatOrchestrator:
    def __init__(
        self,
        model_router: ModelRouter,
        skill_service: SkillService,
        retrieval_service: RetrievalService,
        buffer_memory: LangChainBufferMemoryService,
    ) -> None:
        self.model_router = model_router
        self.skill_service = skill_service
        self.retrieval_service = retrieval_service
        self.buffer_memory = buffer_memory

    async def generate_assistant_reply(
        self,
        chat_id: str,
        history: list[ChatMessage],
        query: str,
        provider: str | None = None,
        model: str | None = None,
    ) -> tuple[str, str, str]:
        selection = self.model_router.resolve(provider=provider, model=model)
        chat_model = self.model_router.build_chat_model(
            provider=selection.provider,
            model=selection.model,
        )
        prompt_messages = [SystemMessage(content=self.skill_service.build_node_prompt("supervisor_node"))]
        conversation_buffer = self.buffer_memory.build_transcript(history)
        if conversation_buffer:
            prompt_messages.append(
                SystemMessage(
                    content=f"Short-term conversation memory:\n{conversation_buffer}"
                )
            )
        retrieval_context = self._build_retrieval_context(query=query, chat_id=chat_id)
        if retrieval_context:
            prompt_messages.append(SystemMessage(content=retrieval_context))
        prompt_messages.extend(self._history_to_langchain_messages(history))

        response = await chat_model.ainvoke(prompt_messages)
        content = self._normalize_content(response.content)
        return content, selection.provider, selection.model

    def _build_retrieval_context(self, query: str, chat_id: str) -> str:
        chunks = self.retrieval_service.retrieve_for_chat(query=query, chat_id=chat_id, limit=5)
        if not chunks:
            return ""

        lines = [
            "Use the following retrieved source context when it is relevant.",
            "Cite or reference source titles when making concrete claims.",
        ]
        for index, chunk in enumerate(chunks, start=1):
            lines.append(f"[Source {index}] {chunk.title}")
            if chunk.uri:
                lines.append(f"URI: {chunk.uri}")
            lines.append(chunk.content)
        return "\n".join(lines)

    def _history_to_langchain_messages(self, history: list[ChatMessage]) -> list:
        messages = []
        for item in history:
            if item.role == "system":
                messages.append(SystemMessage(content=item.content))
            elif item.role == "assistant":
                messages.append(AIMessage(content=item.content))
            else:
                messages.append(HumanMessage(content=item.content))
        return messages

    def _normalize_content(self, content: str | list) -> str:
        if isinstance(content, str):
            return content.strip()
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
        return "\n".join(part.strip() for part in parts if part).strip()
