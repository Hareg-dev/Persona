from procurebrain.agents.nodes.base import BaseAgentNode
from procurebrain.agents.state import AgentGraphState
from procurebrain.application.services.model_router import ModelRouter
from procurebrain.skills.service import SkillService


class QuestionRefinerNode(BaseAgentNode):
    def __init__(self, model_router: ModelRouter, skill_service: SkillService) -> None:
        super().__init__(model_router=model_router, skill_service=skill_service)

    async def run(self, state: AgentGraphState) -> AgentGraphState:
        prompt = (
            f"User question:\n{state.get('query', '')}\n\n"
            f"Conversation buffer:\n{state.get('conversation_buffer', '')}\n\n"
            "Return a refined question followed by up to 10 search queries.\n"
            "Format exactly like:\n"
            "REFINED_QUESTION: ...\n"
            "SEARCH_QUERIES:\n"
            "- query 1\n"
            "- query 2"
        )
        raw = await self.run_prompt(
            "question_refiner_node",
            prompt,
            provider=state.get("provider"),
            model=state.get("model"),
        )
        refined_question, refined_queries = self._parse_output(raw, fallback=state.get("query", ""))
        state["refined_question"] = refined_question
        state["refined_queries"] = refined_queries
        return state

    def _parse_output(self, raw: str, fallback: str) -> tuple[str, list[str]]:
        refined_question = fallback
        queries: list[str] = []
        current_mode = ""
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped.startswith("REFINED_QUESTION:"):
                refined_question = stripped.split(":", 1)[1].strip() or fallback
                current_mode = ""
            elif stripped.startswith("SEARCH_QUERIES"):
                current_mode = "queries"
            elif current_mode == "queries" and stripped.startswith("-"):
                queries.append(stripped[1:].strip())

        if not queries:
            queries = [fallback]
        return refined_question, queries[:10]
