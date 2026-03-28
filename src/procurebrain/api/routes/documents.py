from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_documents() -> dict[str, str]:
    return {"message": "list_documents placeholder"}
