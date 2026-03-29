from typing import TypedDict


class AgentGraphState(TypedDict, total=False):
    chat_id: str
    query: str
    conversation_buffer: str
    retrieved_context: str
    refined_question: str
    refined_queries: list[str]
    search_results: list[dict]
    plan: str
    research_notes: str
    analysis: str
    response: str
    extracted_entities: list[dict]
    knowledge_graph_edges: list[dict]
    mindmap_branches: dict[str, list[str]]
    mindmap_markdown: str
    mindmap_mermaid: str
    artifact_paths: dict[str, str]
    tts_script: dict
