from fastapi import APIRouter, Depends

from procurebrain.agents.state import AgentGraphState
from procurebrain.api.deps import get_run_research_brief_use_case
from procurebrain.application.use_cases.run_research_brief import (
    RunResearchBriefRequest,
    RunResearchBriefUseCase,
)

router = APIRouter()


@router.post("/brief", response_model=dict)
async def run_research_brief(
    request: RunResearchBriefRequest,
    use_case: RunResearchBriefUseCase = Depends(get_run_research_brief_use_case),
) -> AgentGraphState:
    return await use_case.execute(request)
