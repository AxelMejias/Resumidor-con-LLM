# Text Summarizer API

[![Tests](https://github.com/AxelMejias/Resumidor-con-LLM/actions/workflows/tests.yml/badge.svg)](https://github.com/AxelMejias/Resumidor-con-LLM/actions/workflows/tests.yml)

A small FastAPI service that summarizes text using an LLM API (Groq).

**Status:** small learning project, working and tested.

## Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/summarize` | Takes `text`, `max_words` (optional, 10-500, default 100) and `language` (optional, default English). Returns the summary. |
| `GET` | `/health` | Returns `{"status": "ok"}`. |

## Run locally

Requires Python 3.12+ and a [Groq API key](https://console.groq.com/keys).

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
  -d '{"text": "Last summer, my family and I decided to take a wonderful trip to a small village near the mountains. We woke up very early in the morning...", "max_words": 30, "language": "Portuguese"}'
```

```json
{"summary": "No verão passado, viajei com a família a uma vila montanhosa. Partimos cedo, saboreamos café, vimos animais e rios, e chegamos felizes à nossa cabana de madeira."}
```

With `"language": "Spanish"`:

```json
{"summary": "El verano pasado, mi familia y yo visitamos un pueblo montañoso. Tomamos café, la camioneta y condujimos. Vimos animales y ríos; al llegar a la cabaña, estuvimos felices y emocionados."}
```

## Configuration

All settings come from environment variables (or a `.env` file):

| Variable | Default |
|---|---|
| `GROQ_API_KEY` | (required) |
| `GROQ_MODEL` | `openai/gpt-oss-20b` |
| `REQUEST_TIMEOUT` | `30` seconds |
| `MAX_TEXT_CHARS` | `10000` |
| `RATE_LIMIT_REQUESTS` | `10` |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` |

## Tests

Tests use a fake LLM client, so they run without network access or an API key.

```bash
pytest
```

## Technical decisions

- **Provider isolated in one file.** `app/llm_client.py` is the only module that talks to the provider. Routes have no logic, and the service builds the prompt without knowing who answers it. Groq is OpenAI-compatible, so switching to OpenAI is a config change; switching to another SDK means touching only that file.
- **Provider errors mapped to HTTP codes.** Raw provider errors never reach the user:

  | Provider failure | Response |
  |---|---|
  | Timeout | `504` |
  | Provider rate limit | `503` |
  | Invalid key or unknown model | `502` |
  | Empty summary or any other error | `502` |

- **Input validation.** Empty or whitespace-only text, text over the limit and out-of-range `max_words` are rejected with `422` before calling the LLM, so no quota is spent on them.
- **Rate limiting per client IP**, with a sliding window (`429` when exceeded).
- **Tests without network**, using FastAPI dependency overrides to inject a fake client.
- **No user text in logs**: only the error type is logged.

## Limitations

- No user authentication.
- The rate limiter lives in memory: it works for a single process and resets on restart.
- Clients are identified by IP: behind a proxy or Docker port mapping, many clients may share one limit.
- No caching of repeated requests.
- `language` only accepts plain words because it goes into the system prompt. The prompt tells the model to treat the input as text to summarize, but prompt injection can't be fully ruled out. The service only returns text; it never executes anything.
