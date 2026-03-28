from fastapi import APIRouter

from procurebrain.api.routes.agents import router as agents_router
from procurebrain.api.routes.chat import router as chat_router
from procurebrain.api.routes.documents import router as documents_router
from procurebrain.api.routes.health import router as health_router
from procurebrain.api.routes.sessions import router as sessions_router
from procurebrain.api.routes.sources import router as sources_router

router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(chat_router, prefix="/api/v1/chats", tags=["chat"])
router.include_router(sessions_router, prefix="/api/v1/sessions", tags=["sessions"])
router.include_router(sources_router, prefix="/api/v1/sources", tags=["sources"])
router.include_router(documents_router, prefix="/api/v1/documents", tags=["documents"])
router.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
