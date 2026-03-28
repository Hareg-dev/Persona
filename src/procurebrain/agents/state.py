from typing import TypedDict


class AgentGraphState(TypedDict, total=False):
    chat_id: str
    query: str
    conversation_buffer: str
    retrieved_context: str
    plan: str
    research_notes: str
    analysis: str
    response: str
