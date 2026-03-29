from pydantic import BaseModel


class ResearchGraphEdgeResponse(BaseModel):
    source: str
    target: str
    relation: str | None = None
    evidence: str | None = None


class ResearchEntityResponse(BaseModel):
    name: str
    category: str
    note: str | None = None


class SearchResultResponse(BaseModel):
    query: str
    title: str | None = None
    url: str | None = None
    source_id: str | None = None
    error: str | None = None
    reused: bool | None = None


class ResearchArtifactPathsResponse(BaseModel):
    research_brief: str | None = None
    mindmap_markdown: str | None = None
    mindmap_mermaid: str | None = None
    knowledge_graph_chart: str | None = None
    knowledge_graph_image: str | None = None
    tts_request: str | None = None
    audio_file: str | None = None


class TtsScriptResponse(BaseModel):
    language: str
    tone: str
    text: str


class ResearchBriefResponse(BaseModel):
    chat_id: str
    query: str
    refined_question: str | None = None
    refined_queries: list[str]
    search_results: list[SearchResultResponse]
    plan: str | None = None
    research_notes: str | None = None
    analysis: str | None = None
    response: str | None = None
    extracted_entities: list[ResearchEntityResponse]
    knowledge_graph_edges: list[ResearchGraphEdgeResponse]
    mindmap_branches: dict[str, list[str]]
    mindmap_markdown: str | None = None
    mindmap_mermaid: str | None = None
    tts_script: TtsScriptResponse | None = None
    artifact_paths: ResearchArtifactPathsResponse
