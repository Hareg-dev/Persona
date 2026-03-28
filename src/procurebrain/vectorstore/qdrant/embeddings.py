from procurebrain.application.services.model_router import ModelRouter
from procurebrain.config.settings import settings


class EmbeddingService:
    def __init__(self, model_router: ModelRouter) -> None:
        self.model_router = model_router

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        embedding_model = self.model_router.build_embedding_model(
            provider=settings.embedding_provider,
            model=settings.embedding_model_name,
        )
        return embedding_model.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        embedding_model = self.model_router.build_embedding_model(
            provider=settings.embedding_provider,
            model=settings.embedding_model_name,
        )
        return embedding_model.embed_query(text)
