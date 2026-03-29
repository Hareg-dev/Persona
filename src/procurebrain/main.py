from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from procurebrain.api.router import router
from procurebrain.config.logging import configure_logging
from procurebrain.core.exceptions import ExternalServiceError, ProcureBrainError, VectorStoreError
from procurebrain.persistence.mongodb.indexes import ensure_indexes
from procurebrain.vectorstore.qdrant.client import validate_qdrant_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger = logging.getLogger(__name__)
    try:
        await ensure_indexes()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Mongo startup preparation failed: %s", exc)
    try:
        validate_qdrant_connection()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Qdrant startup validation failed: %s", exc)
    yield


app = FastAPI(title="ProcureBrain", version="0.1.0", lifespan=lifespan)
app.include_router(router)


@app.exception_handler(ExternalServiceError)
async def handle_external_service_error(_, exc: ExternalServiceError):
    return JSONResponse(status_code=502, content={"detail": str(exc), "type": exc.__class__.__name__})


@app.exception_handler(VectorStoreError)
async def handle_vector_store_error(_, exc: VectorStoreError):
    return JSONResponse(status_code=503, content={"detail": str(exc), "type": exc.__class__.__name__})


@app.exception_handler(ProcureBrainError)
async def handle_procurebrain_error(_, exc: ProcureBrainError):
    return JSONResponse(status_code=500, content={"detail": str(exc), "type": exc.__class__.__name__})
