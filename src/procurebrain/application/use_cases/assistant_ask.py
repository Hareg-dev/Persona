from fastapi import HTTPException, status

from procurebrain.application.orchestrators.research_orchestrator import ResearchOrchestrator
from procurebrain.application.services.media_output_service import MediaOutputService
from procurebrain.application.services.model_router import ModelRouter
from procurebrain.domain.chat.entities import utc_now
from procurebrain.domain.chat.schemas import (
    AssistantAskRequest,
    AssistantAskResponse,
    ChatSelectionMode,
    ChatSessionResponse,
    ChatIntent,
    MessageResponse,
    ResolvedModelResponse,
)
from procurebrain.domain.chat.service import ChatDomainService
from procurebrain.domain.intelligence.schemas import (
    ResearchArtifactPathsResponse,
    ResearchBriefResponse,
    ResearchEntityResponse,
    ResearchGraphEdgeResponse,
    SearchResultResponse,
    TtsScriptResponse,
)
from procurebrain.memory.artifacts import ArtifactStore
from procurebrain.memory.buffer import LangChainBufferMemoryService
from procurebrain.persistence.repositories.chat_repository import ChatRepository
from procurebrain.persistence.repositories.message_repository import MessageRepository


class AssistantAskUseCase:
    def __init__(
        self,
        chat_repository: ChatRepository,
        message_repository: MessageRepository,
        domain_service: ChatDomainService,
        research_orchestrator: ResearchOrchestrator,
        artifact_store: ArtifactStore,
        model_router: ModelRouter,
        buffer_memory: LangChainBufferMemoryService,
        media_output_service: MediaOutputService,
    ) -> None:
        self.chat_repository = chat_repository
        self.message_repository = message_repository
        self.domain_service = domain_service
        self.research_orchestrator = research_orchestrator
        self.artifact_store = artifact_store
        self.model_router = model_router
        self.buffer_memory = buffer_memory
        self.media_output_service = media_output_service

    async def execute(self, request: AssistantAskRequest) -> AssistantAskResponse:
        chat = await self._resolve_chat(request)
        selection = self.model_router.resolve_for_runtime_choice(
            choice=request.model_choice.value,
            model=request.model,
        )

        user_message = self.domain_service.create_message(
            chat_id=chat.id or "",
            content=request.query,
            role="user",
            provider=selection.provider,
            model=selection.model,
        )
        saved_user = await self.message_repository.create(user_message)
        self.artifact_store.save_message(
            chat_id=chat.id or "",
            role=saved_user.role,
            content=saved_user.content,
            message_id=saved_user.id or "",
            metadata={"provider": saved_user.provider, "model": saved_user.model},
        )

        history = await self.message_repository.list_by_chat_id(chat.id or "")
        conversation_buffer = self.buffer_memory.build_transcript(history, max_messages=20)

        research = None
        assistant_response = None
        if request.intent in {ChatIntent.QUERY, ChatIntent.RESEARCH}:
            state = await self.research_orchestrator.run(
                chat_id=chat.id or "",
                query=request.query,
                conversation_buffer=conversation_buffer,
                provider=selection.provider,
                model=selection.model,
            )
            research = self._to_research_response(state)
            if request.export_format.value == "pdf" and research.response:
                pdf_path = self.media_output_service.save_optional_pdf(
                    output_dir=f"./data/artifacts/{chat.id or ''}/research_outputs",
                    filename="research_brief.pdf",
                    content=research.response,
                )
                research.artifact_paths.research_pdf = str(pdf_path) if pdf_path else None
            if not request.include_audio:
                research.artifact_paths.audio_file = ""
                research.artifact_paths.tts_request = ""
            if not request.include_images:
                research.artifact_paths.knowledge_graph_image = ""
            assistant_message = self.domain_service.create_message(
                chat_id=chat.id or "",
                content=research.response or "",
                role="assistant",
                provider=selection.provider,
                model=selection.model,
            )
            saved_assistant = await self.message_repository.create(assistant_message)
            self.artifact_store.save_message(
                chat_id=chat.id or "",
                role=saved_assistant.role,
                content=saved_assistant.content,
                message_id=saved_assistant.id or "",
                metadata={
                    "provider": saved_assistant.provider,
                    "model": saved_assistant.model,
                    "export_format": request.export_format.value,
                    "include_audio": request.include_audio,
                    "include_images": request.include_images,
                },
            )
            assistant_response = MessageResponse(
                id=saved_assistant.id or "",
                chat_id=saved_assistant.chat_id,
                role=saved_assistant.role,
                content=saved_assistant.content,
                provider=saved_assistant.provider,
                model=saved_assistant.model,
                created_at=saved_assistant.created_at,
            )

        await self.chat_repository.touch(chat.id or "", utc_now())
        updated_chat = await self.chat_repository.get_by_id(chat.id or "")
        if updated_chat is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Chat session could not be reloaded after processing.",
            )

        return AssistantAskResponse(
            chat=ChatSessionResponse(
                id=updated_chat.id or "",
                title=updated_chat.title,
                user_id=updated_chat.user_id,
                status=updated_chat.status,
                created_at=updated_chat.created_at,
                updated_at=updated_chat.updated_at,
            ),
            user_message=MessageResponse(
                id=saved_user.id or "",
                chat_id=saved_user.chat_id,
                role=saved_user.role,
                content=saved_user.content,
                provider=saved_user.provider,
                model=saved_user.model,
                created_at=saved_user.created_at,
            ),
            assistant_message=assistant_response,
            research=research,
            resolved_model=ResolvedModelResponse(
                provider=selection.provider,
                model=selection.model,
            ),
        )

    async def _resolve_chat(self, request: AssistantAskRequest):
        if request.chat_mode == ChatSelectionMode.USE_EXISTING:
            if not request.chat_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="chat_id is required when chat_mode is use_existing.",
                )
            chat = await self.chat_repository.get_by_id(request.chat_id)
            if chat is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chat session '{request.chat_id}' was not found.",
                )
            return chat

        if request.chat_mode == ChatSelectionMode.AUTO_LATEST:
            if request.chat_id:
                chat = await self.chat_repository.get_by_id(request.chat_id)
                if chat is not None:
                    return chat
            latest = await self.chat_repository.get_latest_for_user(user_id=request.user_id)
            if latest is not None:
                return latest

        title = (request.chat_title or self._derive_title(request.query)).strip()
        chat = self.domain_service.create_session(title=title, user_id=request.user_id)
        return await self.chat_repository.create(chat)

    def _derive_title(self, query: str) -> str:
        compact = " ".join(query.split())
        return compact[:80] if len(compact) <= 80 else compact[:77] + "..."

    def _to_research_response(self, state) -> ResearchBriefResponse:
        return ResearchBriefResponse(
            chat_id=state.get("chat_id", ""),
            query=state.get("query", ""),
            refined_question=state.get("refined_question"),
            refined_queries=state.get("refined_queries", []),
            search_results=[
                SearchResultResponse(**item)
                for item in state.get("search_results", [])
            ],
            plan=state.get("plan"),
            research_notes=state.get("research_notes"),
            analysis=state.get("analysis"),
            response=state.get("response"),
            extracted_entities=[
                ResearchEntityResponse(**item)
                for item in state.get("extracted_entities", [])
            ],
            knowledge_graph_edges=[
                ResearchGraphEdgeResponse(**item)
                for item in state.get("knowledge_graph_edges", [])
            ],
            mindmap_branches=state.get("mindmap_branches", {}),
            mindmap_markdown=state.get("mindmap_markdown"),
            mindmap_mermaid=state.get("mindmap_mermaid"),
            tts_script=TtsScriptResponse(**state["tts_script"]) if state.get("tts_script") else None,
            artifact_paths=ResearchArtifactPathsResponse(**state.get("artifact_paths", {})),
        )
