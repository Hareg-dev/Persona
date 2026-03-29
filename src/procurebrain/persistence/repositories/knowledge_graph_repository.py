from procurebrain.persistence.mongodb.client import get_database
from procurebrain.persistence.mongodb.collections import KNOWLEDGE_GRAPH


class KnowledgeGraphRepository:
    def __init__(self) -> None:
        self.collection = get_database()[KNOWLEDGE_GRAPH]

    async def save_edges(self, chat_id: str, root_query: str, edges: list[dict]) -> None:
        await self.collection.insert_one(
            {
                "chat_id": chat_id,
                "root_query": root_query,
                "edges": edges,
            }
        )
