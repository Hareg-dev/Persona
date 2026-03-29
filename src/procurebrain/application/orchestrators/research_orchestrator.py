import logging

from langgraph.graph import END, START, StateGraph

from procurebrain.agents.nodes.analyst import AnalystNode
from procurebrain.agents.nodes.planner import PlannerNode
from procurebrain.agents.nodes.question_refiner import QuestionRefinerNode
from procurebrain.agents.nodes.researcher import ResearcherNode
from procurebrain.agents.nodes.writer import WriterNode
from procurebrain.agents.state import AgentGraphState
from procurebrain.agents.tools.web_search import WebSearchTool
from procurebrain.application.services.analysis_structuring import AnalysisStructuringService
from procurebrain.application.services.context_engineering import ContextEngineeringService
from procurebrain.application.services.knowledge_graph_service import KnowledgeGraphService, KnowledgeRelation
from procurebrain.application.services.media_output_service import MediaOutputService
from procurebrain.application.services.mindmap_service import MindmapService
from procurebrain.application.services.model_router import ModelRouter
from procurebrain.domain.sources.service import SourceDomainService
from procurebrain.ingestion.pdf.chunker import TextChunker
from procurebrain.ingestion.web.extractor import WebExtractor
from procurebrain.ingestion.web.fetcher import WebFetcher
from procurebrain.ingestion.web.normalizer import WebNormalizer
from procurebrain.memory.artifacts import ArtifactStore
from procurebrain.memory.buffer import LangChainBufferMemoryService
from procurebrain.persistence.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from procurebrain.persistence.repositories.source_repository import SourceRepository
from procurebrain.skills.service import SkillService
from procurebrain.vectorstore.qdrant.embeddings import EmbeddingService
from procurebrain.vectorstore.qdrant.retriever import QdrantRetriever


class ResearchOrchestrator:
    def __init__(
        self,
        model_router: ModelRouter,
        skill_service: SkillService,
        buffer_memory: LangChainBufferMemoryService,
        web_search_tool: WebSearchTool,
        web_fetcher: WebFetcher,
        web_extractor: WebExtractor,
        web_normalizer: WebNormalizer,
        source_domain_service: SourceDomainService,
        source_repository: SourceRepository,
        text_chunker: TextChunker,
        embedding_service: EmbeddingService,
        retriever: QdrantRetriever,
        artifact_store: ArtifactStore,
        context_engineering: ContextEngineeringService,
        analysis_structuring: AnalysisStructuringService,
        knowledge_graph_service: KnowledgeGraphService,
        knowledge_graph_repository: KnowledgeGraphRepository,
        mindmap_service: MindmapService,
        media_output_service: MediaOutputService,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.question_refiner = QuestionRefinerNode(model_router=model_router, skill_service=skill_service)
        self.planner = PlannerNode(model_router=model_router, skill_service=skill_service)
        self.researcher = ResearcherNode(model_router=model_router, skill_service=skill_service)
        self.analyst = AnalystNode(model_router=model_router, skill_service=skill_service)
        self.writer = WriterNode(model_router=model_router, skill_service=skill_service)
        self.buffer_memory = buffer_memory
        self.web_search_tool = web_search_tool
        self.web_fetcher = web_fetcher
        self.web_extractor = web_extractor
        self.web_normalizer = web_normalizer
        self.source_domain_service = source_domain_service
        self.source_repository = source_repository
        self.text_chunker = text_chunker
        self.embedding_service = embedding_service
        self.retriever = retriever
        self.artifact_store = artifact_store
        self.context_engineering = context_engineering
        self.analysis_structuring = analysis_structuring
        self.knowledge_graph_service = knowledge_graph_service
        self.knowledge_graph_repository = knowledge_graph_repository
        self.mindmap_service = mindmap_service
        self.media_output_service = media_output_service
        self.graph = self._build_graph()

    async def run(
        self,
        chat_id: str,
        query: str,
        conversation_buffer: str = "",
        provider: str | None = None,
        model: str | None = None,
    ) -> AgentGraphState:
        compressed_context = conversation_buffer
        if conversation_buffer:
            compressed_context = self.context_engineering._compress(conversation_buffer, "")
        initial_state: AgentGraphState = {
            "chat_id": chat_id,
            "query": query,
            "provider": provider or "",
            "model": model or "",
            "conversation_buffer": compressed_context,
        }
        self.logger.info("Starting research workflow for chat_id=%s query=%s", chat_id, query[:120])
        state = await self.graph.ainvoke(initial_state)
        await self._export_research_artifacts(state)
        self.logger.info("Completed research workflow for chat_id=%s", chat_id)
        return state

    def _build_graph(self):
        graph = StateGraph(AgentGraphState)
        graph.add_node("question_refiner", self.question_refiner.run)
        graph.add_node("site_search", self._site_search_node)
        graph.add_node("planner", self.planner.run)
        graph.add_node("researcher", self.researcher.run)
        graph.add_node("analyst", self.analyst.run)
        graph.add_node("writer", self.writer.run)
        graph.add_edge(START, "question_refiner")
        graph.add_edge("question_refiner", "site_search")
        graph.add_edge("site_search", "planner")
        graph.add_edge("planner", "researcher")
        graph.add_edge("researcher", "analyst")
        graph.add_edge("analyst", "writer")
        graph.add_edge("writer", END)
        return graph.compile()

    async def _site_search_node(self, state: AgentGraphState) -> AgentGraphState:
        refined_queries = state.get("refined_queries", [])[:10]
        chat_id = state.get("chat_id")
        unique_urls: set[str] = set()
        collected_results: list[dict] = []
        context_parts: list[str] = []

        for query in refined_queries:
            search_results = self.web_search_tool.search(query, max_results=5)
            for result in search_results:
                url = result.get("url")
                if not url or url in unique_urls or len(unique_urls) >= 10:
                    continue
                unique_urls.add(url)
                try:
                    existing = await self.source_repository.get_by_uri(uri=url, chat_id=chat_id)
                    if existing is not None:
                        collected_results.append(
                            {
                                "query": query,
                                "title": existing.title,
                                "url": existing.uri,
                                "source_id": existing.id,
                                "reused": True,
                            }
                        )
                        context_parts.append(f"{existing.title}\n{existing.content[:2000]}")
                        continue

                    html = await self.web_fetcher.fetch_text(url)
                    title, content = self.web_extractor.extract(html, url)
                    metadata = self.web_normalizer.normalize_metadata(url)
                    source = self.source_domain_service.create_web_source(
                        url=url,
                        title=title,
                        content=content,
                        chat_id=chat_id,
                        metadata={"search_query": query, **metadata},
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
                    collected_results.append(
                        {
                            "query": query,
                            "title": saved.title,
                            "url": saved.uri,
                            "source_id": saved.id,
                            "reused": False,
                        }
                    )
                    context_parts.append(f"{saved.title}\n{saved.content[:2000]}")
                except Exception as exc:
                    self.logger.warning("Site search fetch failed for url=%s error=%s", url, exc)
                    collected_results.append({"query": query, "url": url, "error": str(exc)})

        state["search_results"] = collected_results
        state["retrieved_context"] = "\n\n".join(context_parts[:10])
        return state

    async def _export_research_artifacts(self, state: AgentGraphState) -> None:
        chat_id = state.get("chat_id", "global")
        query = state.get("refined_question") or state.get("query") or "research"
        output_dir = f"./data/artifacts/{chat_id}/research_outputs"
        response = state.get("response", "")
        analysis = state.get("analysis", "")
        structured = await self.analysis_structuring.structure_with_llm(
            text=analysis or response,
            root_query=query,
        )

        brief_path = self.media_output_service.save_markdown(
            output_dir=output_dir,
            filename="research_brief.md",
            content=response or analysis,
        )

        branches = self.mindmap_service.build_branches_from_sections(structured.sections)
        if not branches:
            branches = {
                "Question": [query],
                "Plan": [state.get("plan", "")],
                "Research": [state.get("research_notes", "")],
                "Analysis": [analysis],
            }
        mindmap_md = self.mindmap_service.build_markdown_mindmap("Research Mindmap", branches)
        mindmap_mermaid = self.mindmap_service.build_mermaid_mindmap("Research Mindmap", branches)
        mindmap_md_path = self.media_output_service.save_markdown(output_dir, "mindmap.md", mindmap_md)
        mindmap_mermaid_path = self.media_output_service.save_mermaid(
            output_dir, "mindmap.mmd", mindmap_mermaid
        )
        state["mindmap_markdown"] = mindmap_md
        state["mindmap_mermaid"] = mindmap_mermaid
        state["mindmap_branches"] = branches
        state["extracted_entities"] = [
            {"name": item.name, "category": item.category, "note": item.note}
            for item in structured.entities
        ]

        relations: list[KnowledgeRelation] = list(structured.relations)
        for result in state.get("search_results", []):
            title = result.get("title")
            if title:
                relations.append(
                    KnowledgeRelation(
                        source=query,
                        relation="researched_from",
                        target=title,
                        evidence=result.get("url"),
                    )
                )
        if relations:
            self.knowledge_graph_service.add_relations(relations)
            edges = self.knowledge_graph_service.export_edges()
            state["knowledge_graph_edges"] = edges
            await self.knowledge_graph_repository.save_edges(
                chat_id=chat_id,
                root_query=query,
                edges=edges,
            )
            labels = [edge["target"] for edge in edges]
            values = [1.0 for _ in edges]
            graph_path = None
            if labels:
                graph_path = self.media_output_service.save_bar_chart(
                    output_dir=output_dir,
                    filename="knowledge_graph.html",
                    labels=labels,
                    values=values,
                    title="Knowledge Graph Relations",
                )
                graph_image_path = self.media_output_service.save_optional_chart_image(
                    output_dir=output_dir,
                    filename="knowledge_graph.png",
                    labels=labels,
                    values=values,
                    title="Knowledge Graph Relations",
                )
            state["artifact_paths"] = {
                "research_brief": str(brief_path),
                "mindmap_markdown": str(mindmap_md_path),
                "mindmap_mermaid": str(mindmap_mermaid_path),
                "knowledge_graph_chart": str(graph_path) if graph_path else "",
                "knowledge_graph_image": str(graph_image_path) if graph_image_path else "",
            }
        else:
            state["knowledge_graph_edges"] = []
            state["artifact_paths"] = {
                "research_brief": str(brief_path),
                "mindmap_markdown": str(mindmap_md_path),
                "mindmap_mermaid": str(mindmap_mermaid_path),
                "knowledge_graph_chart": "",
                "knowledge_graph_image": "",
            }

        state["tts_script"] = self.media_output_service.build_tts_script(
            text=response or analysis or query,
            language="en",
            tone="professional",
        )
        tts_path = self.media_output_service.save_tts_request(
            output_dir=output_dir,
            filename="tts_request.json",
            text=response or analysis or query,
            language="en",
            tone="professional",
            voice="default",
        )
        state["artifact_paths"]["tts_request"] = str(tts_path)
        audio_path = self.media_output_service.save_optional_audio(
            output_dir=output_dir,
            filename="speech.mp3",
            text=response or analysis or query,
            language="en",
            tone="professional",
            voice="default",
        )
        state["artifact_paths"]["audio_file"] = str(audio_path) if audio_path else ""
