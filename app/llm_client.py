from functools import lru_cache

import openai
from openai import OpenAI

from app.config import settings


class LLMError(Exception):
    """The LLM provider failed in a way the client can't fix."""


class LLMTimeoutError(LLMError):
    pass


class LLMAuthError(LLMError):
    pass


class LLMRateLimitError(LLMError):
    pass


class LLMEmptyResponseError(LLMError):
    pass


class LLMClient:
    """The only place that knows about the LLM provider."""

    def __init__(self):
        self._client = OpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
            timeout=settings.request_timeout,
            max_retries=0,
        )

    def complete(self, system_prompt: str, user_message: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            )
        except openai.APITimeoutError as exc:
            raise LLMTimeoutError() from exc
        except openai.AuthenticationError as exc:
            raise LLMAuthError() from exc
        except openai.RateLimitError as exc:
            raise LLMRateLimitError() from exc
        except openai.APIError as exc:
            raise LLMError() from exc

        if not response.choices:
            return ""
        return response.choices[0].message.content or ""


@lru_cache
def get_llm_client() -> LLMClient:
    return LLMClient()
