from procurebrain.application.orchestrators.chat_orchestrator import ChatOrchestrator
from procurebrain.application.services.model_router import ModelRouter
from procurebrain.application.services.retrieval_service import RetrievalService
from procurebrain.application.use_cases.create_chat import CreateChatUseCase
from procurebrain.application.use_cases.get_chat_history import GetChatHistoryUseCase
from procurebrain.application.use_cases.ingest_pdf import IngestPdfUseCase
from procurebrain.application.use_cases.ingest_url import IngestUrlUseCase
from procurebrain.application.use_cases.send_message import SendMessageUseCase
from procurebrain.domain.chat.service import ChatDomainService
from procurebrain.domain.sources.service import SourceDomainService
from procurebrain.ingestion.pdf.chunker import TextChunker
from procurebrain.ingestion.pdf.loader import PdfLoader
from procurebrain.ingestion.pdf.parser import PdfParser
from procurebrain.ingestion.web.extractor import WebExtractor
from procurebrain.ingestion.web.fetcher import WebFetcher
from procurebrain.ingestion.web.normalizer import WebNormalizer
from procurebrain.persistence.repositories.chat_repository import ChatRepository
from procurebrain.persistence.repositories.message_repository import MessageRepository
from procurebrain.persistence.repositories.source_repository import SourceRepository
from procurebrain.skills.service import SkillService
from procurebrain.vectorstore.qdrant.embeddings import EmbeddingService
from procurebrain.vectorstore.qdrant.retriever import QdrantRetriever


def get_chat_repository() -> ChatRepository:
    return ChatRepository()


def get_message_repository() -> MessageRepository:
    return MessageRepository()


def get_chat_domain_service() -> ChatDomainService:
    return ChatDomainService()


def get_model_router() -> ModelRouter:
    return ModelRouter()


def get_skill_service() -> SkillService:
    return SkillService()


def get_chat_orchestrator() -> ChatOrchestrator:
    return ChatOrchestrator(
        model_router=get_model_router(),
        skill_service=get_skill_service(),
        retrieval_service=get_retrieval_service(),
    )


def get_source_repository() -> SourceRepository:
    return SourceRepository()


def get_source_domain_service() -> SourceDomainService:
    return SourceDomainService()


def get_web_fetcher() -> WebFetcher:
    return WebFetcher()


def get_web_extractor() -> WebExtractor:
    return WebExtractor()


def get_web_normalizer() -> WebNormalizer:
    return WebNormalizer()


def get_pdf_loader() -> PdfLoader:
    return PdfLoader()


def get_pdf_parser() -> PdfParser:
    return PdfParser()


def get_text_chunker() -> TextChunker:
    return TextChunker()


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(model_router=get_model_router())


def get_qdrant_retriever() -> QdrantRetriever:
    return QdrantRetriever()


def get_retrieval_service() -> RetrievalService:
    return RetrievalService(
        embedding_service=get_embedding_service(),
        retriever=get_qdrant_retriever(),
    )


def get_create_chat_use_case() -> CreateChatUseCase:
    return CreateChatUseCase(
        chat_repository=get_chat_repository(),
        domain_service=get_chat_domain_service(),
    )


def get_send_message_use_case() -> SendMessageUseCase:
    return SendMessageUseCase(
        chat_repository=get_chat_repository(),
        message_repository=get_message_repository(),
        domain_service=get_chat_domain_service(),
        chat_orchestrator=get_chat_orchestrator(),
    )


def get_chat_history_use_case() -> GetChatHistoryUseCase:
    return GetChatHistoryUseCase(
        chat_repository=get_chat_repository(),
        message_repository=get_message_repository(),
    )


def get_ingest_url_use_case() -> IngestUrlUseCase:
    return IngestUrlUseCase(
        source_repository=get_source_repository(),
        source_domain_service=get_source_domain_service(),
        web_fetcher=get_web_fetcher(),
        web_extractor=get_web_extractor(),
        web_normalizer=get_web_normalizer(),
        text_chunker=get_text_chunker(),
        embedding_service=get_embedding_service(),
        retriever=get_qdrant_retriever(),
    )


def get_ingest_pdf_use_case() -> IngestPdfUseCase:
    return IngestPdfUseCase(
        source_repository=get_source_repository(),
        source_domain_service=get_source_domain_service(),
        pdf_loader=get_pdf_loader(),
        pdf_parser=get_pdf_parser(),
        text_chunker=get_text_chunker(),
        embedding_service=get_embedding_service(),
        retriever=get_qdrant_retriever(),
    )
