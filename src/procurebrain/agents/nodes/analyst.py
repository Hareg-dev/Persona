from procurebrain.agents.nodes.base import BaseAgentNode
from procurebrain.agents.state import AgentGraphState
from procurebrain.application.services.model_router import ModelRouter
from procurebrain.skills.service import SkillService


class AnalystNode(BaseAgentNode):
    def __init__(self, model_router: ModelRouter, skill_service: SkillService) -> None:
        super().__init__(model_router=model_router, skill_service=skill_service)

    async def run(self, state: AgentGraphState) -> AgentGraphState:
        prompt = (
            f"User query:\n{state.get('refined_question', state.get('query', ''))}\n\n"
            f"Research notes:\n{state.get('research_notes', '')}\n\n"
            "Analyze the findings through a procurement and business lens.\n"
            "Use clear sections with these exact headers when relevant:\n"
            "Findings:\nRisks:\nOpportunities:\nRecommendations:\nMarket:\nTechnology:"
        )
        state["analysis"] = await self.run_prompt(
            "analyst_node",
            prompt,
            provider=state.get("provider"),
            model=state.get("model"),
        )
        return state
