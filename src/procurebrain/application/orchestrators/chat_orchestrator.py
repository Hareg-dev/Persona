from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from procurebrain.application.orchestrators.research_orchestrator import ResearchOrchestrator
from procurebrain.application.services.context_engineering import ContextEngineeringService
from procurebrain.application.services.model_router import ModelRouter
from procurebrain.domain.chat.entities import ChatMessage
from procurebrain.skills.service import SkillService


class ChatOrchestrator:
    def __init__(
        self,
        model_router: ModelRouter,
        skill_service: SkillService,
        context_engineering: ContextEngineeringService,
        research_orchestrator: ResearchOrchestrator | None = None,
    ) -> None:
        self.model_router = model_router
        self.skill_service = skill_service
        self.context_engineering = context_engineering
        self.research_orchestrator = research_orchestrator

    async def generate_assistant_reply(
        self,
        chat_id: str,
        history: list[ChatMessage],
        query: str,
        provider: str | None = None,
        model: str | None = None,
    ) -> tuple[str, str, str]:
        if self._should_run_research_flow(query=query) and self.research_orchestrator is not None:
            research_response = await self._try_research_flow(
                chat_id=chat_id,
                history=history,
                query=query,
                provider=provider,
                model=model,
            )
            if research_response is not None:
                return research_response

        selection = self.model_router.resolve(provider=provider, model=model)
        chat_model = self.model_router.build_chat_model(
            provider=selection.provider,
            model=selection.model,
        )
        context_bundle = self.context_engineering.build_context_bundle(
            chat_id=chat_id,
            query=query,
            history=history,
        )
        prompt_messages = [SystemMessage(content=self.skill_service.build_node_prompt("supervisor_node"))]
        if context_bundle.conversation_buffer:
            prompt_messages.append(
                SystemMessage(
                    content=f"Short-term conversation memory:\n{context_bundle.conversation_buffer}"
                )
            )
        if context_bundle.compressed_summary:
            prompt_messages.append(
                SystemMessage(content=f"Compressed context summary:\n{context_bundle.compressed_summary}")
            )
        if context_bundle.retrieved_context:
            prompt_messages.append(
                SystemMessage(
                    content=(
                        "Use the following retrieved source context when it is relevant.\n"
                        "Cite or reference source titles when making concrete claims.\n"
                        f"{context_bundle.retrieved_context}"
                    )
                )
            )
        prompt_messages.extend(self._history_to_langchain_messages(history))

        response = await chat_model.ainvoke(prompt_messages)
        content = self._normalize_content(response.content)
        return content, selection.provider, selection.model

    async def _try_research_flow(
        self,
        chat_id: str,
        history: list[ChatMessage],
        query: str,
        provider: str | None = None,
        model: str | None = None,
    ) -> tuple[str, str, str] | None:
        try:
            context_bundle = self.context_engineering.build_context_bundle(
                chat_id=chat_id,
                query=query,
                history=history,
            )
            state = await self.research_orchestrator.run(
                chat_id=chat_id,
                query=query,
                conversation_buffer=context_bundle.conversation_buffer,
            )
            response = (state.get("response") or "").strip()
            if response:
                selection = self.model_router.resolve(provider=provider, model=model)
                return response, selection.provider, selection.model
            return None
        except Exception:
            return None

    def _should_run_research_flow(self, query: str) -> bool:
        lowered = query.lower()
        research_signals = [
            "research",
            "analyze",
            "analysis",
            "compare",
            "market",
            "trend",
            "procurement",
            "supplier",
            "vendor",
            "technology",
            "report",
            "find",
            "search",
            "news",
            "explain",
        ]
        return any(signal in lowered for signal in research_signals) or len(query.split()) > 8

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
