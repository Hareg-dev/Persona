from procurebrain.domain.sources.schemas import RetrievedChunkResponse
from procurebrain.vectorstore.qdrant.embeddings import EmbeddingService
from procurebrain.vectorstore.qdrant.retriever import QdrantRetriever


class RetrievalService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        retriever: QdrantRetriever,
    ) -> None:
        self.embedding_service = embedding_service
        self.retriever = retriever

    def retrieve(self, query: str, limit: int = 5) -> list[RetrievedChunkResponse]:
        return self.retrieve_for_chat(query=query, chat_id=None, limit=limit)

    def retrieve_for_chat(
        self,
        query: str,
        chat_id: str | None,
        limit: int = 5,
    ) -> list[RetrievedChunkResponse]:
        query_vector = self.embedding_service.embed_query(query)
        results = self.retriever.search(query_vector=query_vector, limit=limit, chat_id=chat_id)
        return [
            RetrievedChunkResponse(
                source_id=item["source_id"],
                title=item["title"],
                content=item["content"],
                score=item["score"],
                uri=item["uri"],
                chat_id=item.get("chat_id"),
            )
            for item in results
        ]
