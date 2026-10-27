import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.llm_client import (
    LLMAuthError,
    LLMEmptyResponseError,
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from app.routes import router

logger = logging.getLogger(__name__)

LLM_ERROR_RESPONSES = {
    LLMTimeoutError: (504, "The summary service took too long to respond."),
    LLMRateLimitError: (503, "The summary service is busy. Try again later."),
    LLMAuthError: (502, "The summary service is misconfigured."),
    LLMEmptyResponseError: (502, "The summary service returned an empty summary."),
}

app = FastAPI(title="Text Summarizer API")
app.include_router(router)


@app.exception_handler(LLMError)
def handle_llm_error(request: Request, exc: LLMError):
    status_code, detail = LLM_ERROR_RESPONSES.get(
        type(exc), (502, "The summary service failed.")
    )
    # Log only the error type: never the user's text or the provider's raw message.
    logger.warning("LLM error: %s", type(exc).__name__)
    return JSONResponse(status_code=status_code, content={"detail": detail})
