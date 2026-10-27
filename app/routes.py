from fastapi import APIRouter, Depends

from app import service
from app.llm_client import LLMClient, get_llm_client
from app.rate_limit import check_rate_limit
from app.schemas import SummarizeRequest, SummarizeResponse

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post(
    "/summarize",
    response_model=SummarizeResponse,
    dependencies=[Depends(check_rate_limit)],
)
def summarize(request: SummarizeRequest, llm: LLMClient = Depends(get_llm_client)):
    summary = service.summarize(llm, request.text, request.max_words, request.language)
    return SummarizeResponse(summary=summary)
