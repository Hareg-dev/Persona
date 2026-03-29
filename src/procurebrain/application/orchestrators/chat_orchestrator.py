import logging

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
        self.logger = logging.getLogger(__name__)
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
        context_bundle = self.context_engineering.build_context_bundle(
            chat_id=chat_id,
            query=query,
            history=history,
        )
        if self._should_run_research_flow(query=query) and self.research_orchestrator is not None:
            research_response = await self._try_research_flow(
                chat_id=chat_id,
                history=history,
                query=query,
                provider=provider,
                model=model,
                context_bundle=context_bundle,
            )
            if research_response is not None:
                self.logger.info("Answered via research workflow for chat_id=%s", chat_id)
                return research_response

        selection = self.model_router.resolve(provider=provider, model=model)
        try:
            chat_model = self.model_router.build_chat_model(
                provider=selection.provider,
                model=selection.model,
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
            self.logger.info("Answered via direct supervisor path for chat_id=%s", chat_id)
            return content, selection.provider, selection.model
        except Exception:
            self.logger.exception("Direct supervisor path failed for chat_id=%s", chat_id)
            fallback = self._build_local_fallback_response(query=query, context_bundle=context_bundle)
            return fallback, selection.provider, selection.model

    async def _try_research_flow(
        self,
        chat_id: str,
        history: list[ChatMessage],
        query: str,
        provider: str | None = None,
        model: str | None = None,
        context_bundle=None,
    ) -> tuple[str, str, str] | None:
        try:
            if context_bundle is None:
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
            self.logger.exception("Research workflow failed for chat_id=%s", chat_id)
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

    def _build_local_fallback_response(self, query: str, context_bundle) -> str:
        snippets: list[str] = []
        if context_bundle.retrieved_context:
            snippets.append(context_bundle.retrieved_context[:1200].strip())
        elif context_bundle.compressed_summary:
            snippets.append(context_bundle.compressed_summary[:1200].strip())
        if context_bundle.conversation_buffer and not snippets:
            snippets.append(context_bundle.conversation_buffer[:800].strip())

        evidence = "\n\n".join(part for part in snippets if part).strip()
        if evidence:
            return (
                f"I could not reach a live model provider for this turn, so I built a fallback reply from "
                f"your stored context.\n\n"
                f"Question:\n{query}\n\n"
                "Available context:\n"
                f"{evidence}\n\n"
                "Best next step:\n"
                "Add more sources through the research or ingestion endpoints, then retry the question for a fuller answer."
            )
        return (
            f"I could not reach a live model provider for this turn, and there was not enough saved context "
            f"to synthesize a grounded answer yet.\n\nQuestion:\n{query}\n\n"
            "Best next step:\n"
            "Ingest a few relevant URLs or run the research brief endpoint to collect source material, then retry."
        )
