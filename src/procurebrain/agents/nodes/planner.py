from procurebrain.agents.nodes.base import BaseAgentNode
from procurebrain.agents.state import AgentGraphState
from procurebrain.application.services.model_router import ModelRouter
from procurebrain.skills.service import SkillService


class PlannerNode(BaseAgentNode):
    def __init__(self, model_router: ModelRouter, skill_service: SkillService) -> None:
        super().__init__(model_router=model_router, skill_service=skill_service)

    async def run(self, state: AgentGraphState) -> AgentGraphState:
        prompt = (
            f"User query:\n{state.get('query', '')}\n\n"
            f"Conversation buffer:\n{state.get('conversation_buffer', '')}\n\n"
            "Create a clear research plan for the next nodes."
        )
        state["plan"] = await self.run_prompt("planner_node", prompt)
        return state
