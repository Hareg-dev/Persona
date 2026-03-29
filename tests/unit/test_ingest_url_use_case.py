import asyncio

from procurebrain.application.use_cases.ingest_url import IngestUrlUseCase
from procurebrain.domain.sources.schemas import IngestUrlRequest
from procurebrain.domain.sources.service import SourceDomainService
from procurebrain.ingestion.pdf.chunker import TextChunker


class FakeSourceRepository:
    async def create(self, source):
        source.id = "source-1"
        return source


class FakeFetcher:
    async def fetch_text(self, url: str, timeout: float = 20.0) -> str:
        return "<html><head><title>Example</title></head><body><p>Hello world</p></body></html>"


class FakeExtractor:
    def extract(self, html: str, url: str | None = None):
        return ("Example", "Hello world")


class FakeNormalizer:
    def normalize_metadata(self, url: str):
        return {"domain": "example.com"}


class FakeEmbeddingService:
    def embed_texts(self, texts):
        return [[0.1, 0.2] for _ in texts]


class FakeRetriever:
    def upsert_chunks(self, **kwargs):
        return None


class FakeArtifactStore:
    def save_source(self, **kwargs):
        return None


def test_ingest_url_returns_saved_source():
    use_case = IngestUrlUseCase(
        source_repository=FakeSourceRepository(),
        source_domain_service=SourceDomainService(),
        web_fetcher=FakeFetcher(),
        web_extractor=FakeExtractor(),
        web_normalizer=FakeNormalizer(),
        text_chunker=TextChunker(),
        embedding_service=FakeEmbeddingService(),
        retriever=FakeRetriever(),
        artifact_store=FakeArtifactStore(),
    )

    result = asyncio.run(use_case.execute(IngestUrlRequest(url="https://example.com")))
    assert result.id == "source-1"
    assert result.title == "Example"
