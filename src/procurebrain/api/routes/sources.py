from fastapi import APIRouter, Depends

from procurebrain.api.deps import get_ingest_pdf_use_case, get_ingest_url_use_case
from procurebrain.application.use_cases.ingest_pdf import IngestPdfUseCase
from procurebrain.application.use_cases.ingest_url import IngestUrlUseCase
from procurebrain.domain.sources.schemas import IngestPdfRequest, IngestUrlRequest, SourceResponse

router = APIRouter()


@router.post("/url", response_model=SourceResponse, status_code=201)
async def ingest_url(
    request: IngestUrlRequest,
    use_case: IngestUrlUseCase = Depends(get_ingest_url_use_case),
) -> SourceResponse:
    return await use_case.execute(request)


@router.post("/pdf", response_model=SourceResponse, status_code=201)
async def ingest_pdf(
    request: IngestPdfRequest,
    use_case: IngestPdfUseCase = Depends(get_ingest_pdf_use_case),
) -> SourceResponse:
    return await use_case.execute(request)
