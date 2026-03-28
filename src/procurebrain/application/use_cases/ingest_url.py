from procurebrain.domain.sources.schemas import IngestUrlRequest, SourceResponse
from procurebrain.domain.sources.service import SourceDomainService
from procurebrain.ingestion.pdf.chunker import TextChunker
from procurebrain.ingestion.web.extractor import WebExtractor
from procurebrain.ingestion.web.fetcher import WebFetcher
from procurebrain.ingestion.web.normalizer import WebNormalizer
from procurebrain.memory.artifacts import ArtifactStore
from procurebrain.persistence.repositories.source_repository import SourceRepository
from procurebrain.vectorstore.qdrant.embeddings import EmbeddingService
from procurebrain.vectorstore.qdrant.retriever import QdrantRetriever


class IngestUrlUseCase:
    def __init__(
        self,
        source_repository: SourceRepository,
        source_domain_service: SourceDomainService,
        web_fetcher: WebFetcher,
        web_extractor: WebExtractor,
        web_normalizer: WebNormalizer,
        text_chunker: TextChunker,
        embedding_service: EmbeddingService,
        retriever: QdrantRetriever,
        artifact_store: ArtifactStore,
    ) -> None:
        self.source_repository = source_repository
        self.source_domain_service = source_domain_service
        self.web_fetcher = web_fetcher
        self.web_extractor = web_extractor
        self.web_normalizer = web_normalizer
        self.text_chunker = text_chunker
        self.embedding_service = embedding_service
        self.retriever = retriever
        self.artifact_store = artifact_store

    async def execute(self, request: IngestUrlRequest) -> SourceResponse:
        html = await self.web_fetcher.fetch_text(str(request.url))
        title, content = self.web_extractor.extract(html, str(request.url))
        metadata = self.web_normalizer.normalize_metadata(str(request.url))

        source = self.source_domain_service.create_web_source(
            url=str(request.url),
            title=title,
            content=content,
            chat_id=request.chat_id,
            metadata=metadata,
        )
        saved = await self.source_repository.create(source)

        chunks = self.text_chunker.chunk(saved.content)
        vectors = self.embedding_service.embed_texts(chunks) if chunks else []
        self.retriever.upsert_chunks(
            source_id=saved.id or "",
            title=saved.title,
            chunks=chunks,
            vectors=vectors,
            uri=saved.uri,
            chat_id=saved.chat_id,
        )
        self.artifact_store.save_source(
            source_id=saved.id or "",
            title=saved.title,
            content=saved.content,
            chat_id=saved.chat_id,
            metadata={"uri": saved.uri, **(saved.metadata or {})},
        )

        return SourceResponse(
            id=saved.id or "",
            source_type=saved.source_type,
            title=saved.title,
            uri=saved.uri,
            chat_id=saved.chat_id,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )
