from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from procurebrain.config.settings import settings
from procurebrain.core.exceptions import VectorStoreError


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
    )


def ensure_collection(vector_size: int) -> None:
    try:
        client = get_qdrant_client()
        collections = {item.name for item in client.get_collections().collections}
        if settings.qdrant_collection not in collections:
            client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
    except Exception as exc:  # noqa: BLE001
        raise VectorStoreError(f"Failed to ensure Qdrant collection: {exc}") from exc


def validate_qdrant_connection() -> None:
    try:
        get_qdrant_client().get_collections()
    except Exception as exc:  # noqa: BLE001
        raise VectorStoreError(f"Failed to connect to Qdrant: {exc}") from exc


def qdrant_is_ready() -> bool:
    validate_qdrant_connection()
    return True
