from fastapi import APIRouter

router = APIRouter()


@router.get("/runs")
def list_agent_runs() -> dict[str, str]:
    return {"message": "list_agent_runs placeholder"}
