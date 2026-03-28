from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_sessions() -> dict[str, str]:
    return {"message": "list_sessions placeholder"}
