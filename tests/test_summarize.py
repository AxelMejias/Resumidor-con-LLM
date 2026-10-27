import pytest

from app.llm_client import (
    LLMAuthError,
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
)


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_summarize_returns_summary(client, fake_llm):
    response = client.post(
        "/summarize", json={"text": "Some long text.", "max_words": 50, "language": "Spanish"}
    )

    assert response.status_code == 200
    assert response.json() == {"summary": "A short summary."}
    system_prompt, user_message = fake_llm.calls[0]
    assert "Spanish" in system_prompt
    assert "50 words" in system_prompt
    assert user_message == "Some long text."


@pytest.mark.parametrize(
    ("error", "status_code"),
    [
        (LLMTimeoutError(), 504),
        (LLMRateLimitError(), 503),
        (LLMAuthError(), 502),
        (LLMError(), 502),
    ],
)
def test_provider_errors_are_mapped(client, fake_llm, error, status_code):
    fake_llm.error = error

    response = client.post("/summarize", json={"text": "Some text."})

    assert response.status_code == status_code
    assert "detail" in response.json()


def test_empty_summary_is_an_error(client, fake_llm):
    fake_llm.reply = "   "

    response = client.post("/summarize", json={"text": "Some text."})

    assert response.status_code == 502


def test_rate_limit_blocks_extra_requests(client):
    for _ in range(3):
        assert client.post("/summarize", json={"text": "Some text."}).status_code == 200

    response = client.post("/summarize", json={"text": "Some text."})

    assert response.status_code == 429
