from procurebrain.agents.nodes.base import BaseAgentNode
from procurebrain.agents.state import AgentGraphState
from procurebrain.application.services.model_router import ModelRouter
from procurebrain.skills.service import SkillService


class AnalystNode(BaseAgentNode):
    def __init__(self, model_router: ModelRouter, skill_service: SkillService) -> None:
        super().__init__(model_router=model_router, skill_service=skill_service)

    async def run(self, state: AgentGraphState) -> AgentGraphState:
        prompt = (
            f"User query:\n{state.get('query', '')}\n\n"
            f"Research notes:\n{state.get('research_notes', '')}\n\n"
            "Analyze the findings through a procurement and business lens."
        )
        state["analysis"] = await self.run_prompt("analyst_node", prompt)
        return state
