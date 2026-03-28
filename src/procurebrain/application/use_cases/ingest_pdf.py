from pathlib import Path

from procurebrain.domain.sources.schemas import IngestPdfRequest, SourceResponse
from procurebrain.domain.sources.service import SourceDomainService
from procurebrain.ingestion.pdf.chunker import TextChunker
from procurebrain.ingestion.pdf.loader import PdfLoader
from procurebrain.ingestion.pdf.parser import PdfParser
from procurebrain.memory.artifacts import ArtifactStore
from procurebrain.persistence.repositories.source_repository import SourceRepository
from procurebrain.vectorstore.qdrant.embeddings import EmbeddingService
from procurebrain.vectorstore.qdrant.retriever import QdrantRetriever


class IngestPdfUseCase:
    def __init__(
        self,
        source_repository: SourceRepository,
        source_domain_service: SourceDomainService,
        pdf_loader: PdfLoader,
        pdf_parser: PdfParser,
        text_chunker: TextChunker,
        embedding_service: EmbeddingService,
        retriever: QdrantRetriever,
        artifact_store: ArtifactStore,
    ) -> None:
        self.source_repository = source_repository
        self.source_domain_service = source_domain_service
        self.pdf_loader = pdf_loader
        self.pdf_parser = pdf_parser
        self.text_chunker = text_chunker
        self.embedding_service = embedding_service
        self.retriever = retriever
        self.artifact_store = artifact_store

    async def execute(self, request: IngestPdfRequest) -> SourceResponse:
        payload = self.pdf_loader.read_bytes(request.file_path)
        content, metadata = self.pdf_parser.parse(payload)
        title = request.title or metadata.get("title") or Path(request.file_path).name

        source = self.source_domain_service.create_pdf_source(
            file_path=request.file_path,
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
