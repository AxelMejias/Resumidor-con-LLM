from functools import lru_cache

from openai import OpenAI

from app.config import settings


class LLMClient:
    """The only place that knows about the LLM provider."""

    def __init__(self):
        self._client = OpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
            timeout=settings.request_timeout,
        )

    def complete(self, system_prompt: str, user_message: str) -> str:
        response = self._client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or ""


@lru_cache
def get_llm_client() -> LLMClient:
    return LLMClient()
