from pydantic import BaseModel, Field

from procurebrain.agents.state import AgentGraphState
from procurebrain.application.orchestrators.research_orchestrator import ResearchOrchestrator


class RunResearchBriefRequest(BaseModel):
    chat_id: str = Field(min_length=1)
    query: str = Field(min_length=1)


class RunResearchBriefUseCase:
    def __init__(self, orchestrator: ResearchOrchestrator) -> None:
        self.orchestrator = orchestrator

    async def execute(self, request: RunResearchBriefRequest) -> AgentGraphState:
        return await self.orchestrator.run(chat_id=request.chat_id, query=request.query)
