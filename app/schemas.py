from pydantic import BaseModel, ConfigDict, Field

from app.config import settings


class SummarizeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    text: str = Field(min_length=1, max_length=settings.max_text_chars)
    max_words: int = Field(default=100, ge=10, le=500)
    language: str = Field(default="English", min_length=2, max_length=30)


class SummarizeResponse(BaseModel):
    summary: str
