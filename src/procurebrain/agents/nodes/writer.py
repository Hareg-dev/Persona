from procurebrain.agents.nodes.base import BaseAgentNode
from procurebrain.agents.state import AgentGraphState
from procurebrain.application.services.model_router import ModelRouter
from procurebrain.skills.service import SkillService


class WriterNode(BaseAgentNode):
    def __init__(self, model_router: ModelRouter, skill_service: SkillService) -> None:
        super().__init__(model_router=model_router, skill_service=skill_service)

    async def run(self, state: AgentGraphState) -> AgentGraphState:
        prompt = (
            f"Conversation buffer:\n{state.get('conversation_buffer', '')}\n\n"
            f"Analysis:\n{state.get('analysis', '')}\n\n"
            f"Retrieved context:\n{state.get('retrieved_context', '')}\n\n"
            "Write the final grounded response."
        )
        state["response"] = await self.run_prompt("writer_node", prompt)
        return state
