import asyncio
from pathlib import Path

from procurebrain.application.orchestrators.research_orchestrator import ResearchOrchestrator
from procurebrain.application.services.analysis_structuring import AnalysisStructuringService
from procurebrain.application.services.context_engineering import ContextEngineeringService
from procurebrain.application.services.knowledge_graph_service import KnowledgeGraphService
from procurebrain.application.services.media_output_service import MediaOutputService
from procurebrain.application.services.mindmap_service import MindmapService
from procurebrain.application.services.model_router import ModelRouter
from procurebrain.application.services.retrieval_service import RetrievalService
from procurebrain.domain.sources.service import SourceDomainService
from procurebrain.ingestion.pdf.chunker import TextChunker
from procurebrain.memory.artifacts import ArtifactStore
from procurebrain.memory.buffer import LangChainBufferMemoryService
from procurebrain.skills.service import SkillService


class FakeSearchTool:
    def search(self, query: str, max_results: int = 5):
        return [{"title": "Example", "url": "https://example.com", "snippet": "demo"}]


class FakeFetcher:
    async def fetch_text(self, url: str, timeout: float = 20.0) -> str:
        return "<html><head><title>Example</title></head><body><p>Hello world</p></body></html>"


class FakeExtractor:
    def extract(self, html: str, url: str | None = None):
        return ("Example", "Hello world procurement technology")


class FakeNormalizer:
    def normalize_metadata(self, url: str):
        return {"domain": "example.com"}


class FakeSourceRepository:
    async def get_by_uri(self, uri: str, chat_id: str | None = None):
        return None

    async def create(self, source):
        source.id = "source-1"
        return source


class FakeEmbeddingService:
    def embed_texts(self, texts):
        return [[0.1, 0.2] for _ in texts]


class FakeRetriever:
    def upsert_chunks(self, **kwargs):
        return None


class FakeArtifactStore(ArtifactStore):
    def __init__(self):
        super().__init__(root_dir="./data/test_artifacts")


class FakeKnowledgeGraphRepository:
    async def save_edges(self, chat_id: str, root_query: str, edges: list[dict]) -> None:
        return None


class FakeModelRouter(ModelRouter):
    def build_chat_model(self, provider=None, model=None):
        class FakeChatModel:
            async def ainvoke(self, messages):
                class Response:
                    content = (
                        "REFINED_QUESTION: Procurement technology trends\n"
                        "SEARCH_QUERIES:\n- procurement technology trends"
                    )

                if isinstance(messages, str):
                    class Response2:
                        content = "{}"
                    return Response2()
                return Response()

        return FakeChatModel()


def test_research_orchestrator_returns_response_state():
    tmp_path = Path("./data/test_artifacts_runtime")
    artifact_store = ArtifactStore(root_dir=str(tmp_path))
    orchestrator = ResearchOrchestrator(
        model_router=FakeModelRouter(),
        skill_service=SkillService(),
        buffer_memory=LangChainBufferMemoryService(),
        web_search_tool=FakeSearchTool(),
        web_fetcher=FakeFetcher(),
        web_extractor=FakeExtractor(),
        web_normalizer=FakeNormalizer(),
        source_domain_service=SourceDomainService(),
        source_repository=FakeSourceRepository(),
        text_chunker=TextChunker(),
        embedding_service=FakeEmbeddingService(),
        retriever=FakeRetriever(),
        artifact_store=artifact_store,
        context_engineering=ContextEngineeringService(
            buffer_memory=LangChainBufferMemoryService(),
            retrieval_service=RetrievalService(
                embedding_service=FakeEmbeddingService(),
                retriever=FakeRetriever(),
            ),
        ),
        analysis_structuring=AnalysisStructuringService(),
        knowledge_graph_service=KnowledgeGraphService(),
        knowledge_graph_repository=FakeKnowledgeGraphRepository(),
        mindmap_service=MindmapService(),
        media_output_service=MediaOutputService(),
    )

    state = asyncio.run(orchestrator.run(chat_id="chat-1", query="Explain procurement tech trends"))
    assert state["refined_question"]
