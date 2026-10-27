import pytest


@pytest.mark.parametrize(
    "payload",
    [
        {"text": ""},
        {"text": "   \n  "},
        {"text": "a" * 10_001},
        {"text": "Some text.", "max_words": 5},
        {"text": "Some text.", "max_words": 501},
        {"text": "Some text.", "language": "x"},
    ],
)
def test_invalid_input_is_rejected(client, fake_llm, payload):
    response = client.post("/summarize", json=payload)

    assert response.status_code == 422
    assert fake_llm.calls == []
