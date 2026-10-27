# Text Summarizer API

A small FastAPI service that summarizes text using an LLM API (Groq).

**Status:** small learning project, work in progress.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env        # then set GROQ_API_KEY
uvicorn app.main:app --reload
```

Interactive docs at http://localhost:8000/docs.

## Run with Docker

```bash
docker build -t text-summarizer-api .
docker run --env-file .env -p 8000:8000 text-summarizer-api
```

## Usage

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Your long text here...", "max_words": 50, "language": "English"}'
```

```json
{"summary": "..."}
```

## Tests

Tests use a fake LLM client, so they run without network access or an API key.

```bash
pytest
```
