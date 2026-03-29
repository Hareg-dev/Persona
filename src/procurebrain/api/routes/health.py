from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from procurebrain.api.deps import get_model_router
from procurebrain.application.services.model_router import ModelRouter
from procurebrain.domain.system.schemas import ComponentStatus, ReadinessResponse
from procurebrain.persistence.mongodb.client import ping_mongo
from procurebrain.vectorstore.qdrant.client import qdrant_is_ready

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/health/ready", response_model=ReadinessResponse)
async def ready(model_router: ModelRouter = Depends(get_model_router)) -> ReadinessResponse | JSONResponse:
    components: list[ComponentStatus] = []

    try:
        mongo_ok = await ping_mongo()
        components.append(ComponentStatus(name="mongo", ok=mongo_ok, detail="connected"))
    except Exception as exc:  # noqa: BLE001
        components.append(ComponentStatus(name="mongo", ok=False, detail=str(exc)))

    try:
        qdrant_ok = qdrant_is_ready()
        components.append(ComponentStatus(name="qdrant", ok=qdrant_ok, detail="connected"))
    except Exception as exc:  # noqa: BLE001
        components.append(ComponentStatus(name="qdrant", ok=False, detail=str(exc)))

    all_ok = all(component.ok for component in components)
    response = ReadinessResponse(
        status="ready" if all_ok else "degraded",
        components=components,
        models=model_router.provider_status(),
    )
    if all_ok:
        return response
    return JSONResponse(status_code=503, content=response.model_dump())
