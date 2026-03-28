from uuid import uuid4

from qdrant_client.models import PointStruct

from procurebrain.config.settings import settings
from procurebrain.vectorstore.qdrant.client import ensure_collection, get_qdrant_client


class QdrantRetriever:
    def upsert_chunks(
        self,
        source_id: str,
        title: str,
        chunks: list[str],
        vectors: list[list[float]],
        uri: str | None = None,
    ) -> None:
        if not chunks or not vectors:
            return

        ensure_collection(vector_size=len(vectors[0]))
        client = get_qdrant_client()
        points = [
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "source_id": source_id,
                    "title": title,
                    "content": chunk,
                    "uri": uri,
                },
            )
            for chunk, vector in zip(chunks, vectors, strict=False)
        ]
        client.upsert(collection_name=settings.qdrant_collection, points=points)

    def search(self, query_vector: list[float], limit: int = 5) -> list[dict]:
        ensure_collection(vector_size=len(query_vector))
        client = get_qdrant_client()
        results = client.search(
            collection_name=settings.qdrant_collection,
            query_vector=query_vector,
            limit=limit,
        )
        return [
            {
                "score": item.score,
                "source_id": item.payload.get("source_id"),
                "title": item.payload.get("title"),
                "content": item.payload.get("content"),
                "uri": item.payload.get("uri"),
            }
            for item in results
        ]
