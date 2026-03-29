from pydantic import BaseModel, Field

from procurebrain.agents.state import AgentGraphState
from procurebrain.application.orchestrators.research_orchestrator import ResearchOrchestrator
from procurebrain.domain.intelligence.schemas import (
    ResearchEntityResponse,
    ResearchArtifactPathsResponse,
    ResearchBriefResponse,
    ResearchGraphEdgeResponse,
    SearchResultResponse,
    TtsScriptResponse,
)


class RunResearchBriefRequest(BaseModel):
    chat_id: str = Field(min_length=1)
    query: str = Field(min_length=1)


class RunResearchBriefUseCase:
    def __init__(self, orchestrator: ResearchOrchestrator) -> None:
        self.orchestrator = orchestrator

    async def execute(self, request: RunResearchBriefRequest) -> ResearchBriefResponse:
        state = await self.orchestrator.run(chat_id=request.chat_id, query=request.query)
        return self._to_response(state)

    def _to_response(self, state: AgentGraphState) -> ResearchBriefResponse:
        return ResearchBriefResponse(
            chat_id=state.get("chat_id", ""),
            query=state.get("query", ""),
            refined_question=state.get("refined_question"),
            refined_queries=state.get("refined_queries", []),
            search_results=[
                SearchResultResponse(**item)
                for item in state.get("search_results", [])
            ],
            plan=state.get("plan"),
            research_notes=state.get("research_notes"),
            analysis=state.get("analysis"),
            response=state.get("response"),
            extracted_entities=[
                ResearchEntityResponse(**item)
                for item in state.get("extracted_entities", [])
            ],
            knowledge_graph_edges=[
                ResearchGraphEdgeResponse(**item)
                for item in state.get("knowledge_graph_edges", [])
            ],
            mindmap_branches=state.get("mindmap_branches", {}),
            mindmap_markdown=state.get("mindmap_markdown"),
            mindmap_mermaid=state.get("mindmap_mermaid"),
            tts_script=TtsScriptResponse(**state["tts_script"]) if state.get("tts_script") else None,
            artifact_paths=ResearchArtifactPathsResponse(**state.get("artifact_paths", {})),
        )
