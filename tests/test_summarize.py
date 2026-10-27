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
