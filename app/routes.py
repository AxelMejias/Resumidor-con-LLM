from fastapi import APIRouter, Depends

from app import service
from app.llm_client import LLMClient, get_llm_client
from app.schemas import SummarizeRequest, SummarizeResponse

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest, llm: LLMClient = Depends(get_llm_client)):
    summary = service.summarize(llm, request.text, request.max_words, request.language)
    return SummarizeResponse(summary=summary)
