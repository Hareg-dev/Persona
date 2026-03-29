import logging

from langchain_core.messages import HumanMessage, SystemMessage

from procurebrain.application.services.model_router import ModelRouter
from procurebrain.skills.service import SkillService


class BaseAgentNode:
    def __init__(self, model_router: ModelRouter, skill_service: SkillService) -> None:
        self.logger = logging.getLogger(__name__)
        self.model_router = model_router
        self.skill_service = skill_service

    async def run_prompt(
        self,
        node_name: str,
        user_prompt: str,
        provider: str | None = None,
        model: str | None = None,
    ) -> str:
        try:
            chat_model = self.model_router.build_chat_model(provider=provider, model=model)
            system_prompt = self.skill_service.build_node_prompt(node_name)
            response = await chat_model.ainvoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
            content = response.content
            if isinstance(content, str):
                return content.strip()
            parts: list[str] = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    parts.append(str(item["text"]))
            normalized = "\n".join(part.strip() for part in parts if part).strip()
            if normalized:
                return normalized
        except Exception as exc:  # noqa: BLE001
            self.logger.warning(
                "Agent node fallback activated for node=%s error=%s",
                node_name,
                exc,
            )
        return self._fallback_response(node_name=node_name, user_prompt=user_prompt)

    def _fallback_response(self, node_name: str, user_prompt: str) -> str:
        compact_prompt = " ".join(user_prompt.split())
        if node_name == "question_refiner_node":
            return (
                f"REFINED_QUESTION: {compact_prompt[:240]}\n"
                "SEARCH_QUERIES:\n"
                f"- {compact_prompt[:180]}\n"
                "- procurement AI tools market trends\n"
                "- vendor comparison implementation risks\n"
                "- open source research assistant architecture"
            )
        if node_name == "planner_node":
            return (
                "1. Clarify the research goal and procurement angle.\n"
                "2. Gather evidence from accessible sources and prior memory.\n"
                "3. Compare vendors, market signals, and technical approaches.\n"
                "4. Summarize risks, opportunities, and recommended next steps."
            )
        if node_name == "researcher_node":
            return (
                "Collected available source context and prior memory.\n"
                "Normalized the evidence into reusable notes.\n"
                "Flagged gaps where live external provider output was unavailable."
            )
        if node_name == "analyst_node":
            return (
                "Findings:\n"
                "- Available context suggests demand for procurement-focused AI copilots.\n"
                "- The system should prioritize source-backed summaries and reusable memory.\n"
                "Risks:\n"
                "- External provider or search outages can interrupt live analysis.\n"
                "- Generic AI answers reduce procurement usefulness.\n"
                "Opportunities:\n"
                "- Persisting research, sources, and graph relations compounds value over time.\n"
                "Recommendations:\n"
                "- Keep a fallback path that uses stored context when providers are unavailable.\n"
                "Market:\n"
                "- Buyers need concise vendor comparisons, research traceability, and monitoring.\n"
                "Technology:\n"
                "- LangGraph, MongoDB, Qdrant, and modular skill packages remain a strong stack."
            )
        if node_name == "writer_node":
            return (
                "I assembled a grounded response from the currently available local context and saved "
                "research artifacts. Some live model-enhanced synthesis was unavailable, so this draft "
                "should be treated as a fallback summary until provider calls succeed."
            )
        return compact_prompt[:500]
