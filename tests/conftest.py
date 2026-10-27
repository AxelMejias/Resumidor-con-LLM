import pytest
from fastapi.testclient import TestClient

from app import rate_limit
from app.llm_client import get_llm_client
from app.main import app


class FakeLLMClient:
    def __init__(self):
        self.reply = "A short summary."
        self.error = None
        self.calls = []

    def complete(self, system_prompt: str, user_message: str) -> str:
        self.calls.append((system_prompt, user_message))
        if self.error:
            raise self.error
        return self.reply


@pytest.fixture
def fake_llm():
    return FakeLLMClient()


@pytest.fixture
def client(fake_llm, monkeypatch):
    monkeypatch.setattr(rate_limit, "rate_limiter", rate_limit.RateLimiter(3, 60))
    app.dependency_overrides[get_llm_client] = lambda: fake_llm
    yield TestClient(app)
    app.dependency_overrides.clear()
