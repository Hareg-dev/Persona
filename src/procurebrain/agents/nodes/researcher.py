from procurebrain.agents.nodes.base import BaseAgentNode
from procurebrain.agents.state import AgentGraphState
from procurebrain.application.services.model_router import ModelRouter
from procurebrain.skills.service import SkillService


class ResearcherNode(BaseAgentNode):
    def __init__(self, model_router: ModelRouter, skill_service: SkillService) -> None:
        super().__init__(model_router=model_router, skill_service=skill_service)

    async def run(self, state: AgentGraphState) -> AgentGraphState:
        prompt = (
            f"Research plan:\n{state.get('plan', '')}\n\n"
            f"Retrieved context:\n{state.get('retrieved_context', '')}\n\n"
            f"Search results summary:\n{state.get('search_results', [])}\n\n"
            "Produce normalized research notes grounded in the retrieved evidence."
        )
        state["research_notes"] = await self.run_prompt(
            "researcher_node",
            prompt,
            provider=state.get("provider"),
            model=state.get("model"),
        )
        return state
