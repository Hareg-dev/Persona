from fastapi import APIRouter

router = APIRouter()


@router.post("/url")
def ingest_url() -> dict[str, str]:
    return {"message": "ingest_url placeholder"}


@router.post("/pdf")
def ingest_pdf() -> dict[str, str]:
    return {"message": "ingest_pdf placeholder"}
