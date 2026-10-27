def test_empty_text_is_rejected(client):
    response = client.post("/summarize", json={"text": ""})

    assert response.status_code == 422


def test_max_words_out_of_range_is_rejected(client):
    response = client.post("/summarize", json={"text": "Some text.", "max_words": 5})

    assert response.status_code == 422
