# Uruguay Guide 🇺🇾

A small, stateless, multilingual AI assistant for people considering Uruguay (residency, nationality, cities, cost of living, banking, ...). React + FastAPI, shipped as one Docker image.

```
User → FastAPI → keyword scope check → optional official-source retrieval → one LLM call → answer (+ sources)
```

- **No LLM for UI or language selection**: static strings live in `frontend/src/i18n/*.json`; the chosen language is stored in `localStorage` and sent with each chat request, where it goes into the (short) system prompt.
- **Scope check** (`backend/app/services/scope.py`): multilingual keyword categories. Clearly unrelated prompts get a local reply, with no LLM call. Ambiguous text goes to the LLM.
- **Official sources** (`backend/app/knowledge/`): for legal categories (nationality, citizenship, residency, immigration, documents, taxes) the backend fetches a curated allowlist of `gub.uy` / `impo.com.uy` / `corteelectoral.gub.uy` pages (cached 6 h, truncated), passes them to the LLM as context and returns them as `sources` with `retrieved_at`. Users can never supply URLs, so there is no SSRF surface. If retrieval fails, links are still returned and the prompt tells the model to say the info must be verified.
- **Cost controls**: message ≤ 2000 chars, last 6 history messages, `max_tokens` cap, short prompt, one completion per question, 10 req/min/IP.
- **LLM provider**: any OpenAI-compatible `/chat/completions` API via `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`. The key stays on the backend.

## Run locally

```bash
cp .env.example .env     # fill in LLM_API_KEY / LLM_BASE_URL / LLM_MODEL
docker compose up --build
# frontend http://localhost:5173  (proxies /api)   backend http://localhost:8000
```

Without Docker:

```bash
cd backend && python3.12 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/uvicorn app.main:app --reload
cd frontend && npm ci && npm run dev
```

## Checks (also run in CI)

```bash
cd backend && ruff check . && pyright && pytest      # tests never call a real LLM
cd frontend && npm run typecheck && npm run build
```

## Production image

```bash
docker build -t uruguay-guide .
docker run -p 8000:8000 --env-file .env uruguay-guide
```

Multi-stage build: Node builds the React app, then Python serves `/api/*` and the static files from one container (no CORS). It honors `$PORT`.

**Render**: create a Web Service from this repo (Docker runtime, free plan; `render.yaml` is provided), set `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, and `TRUST_PROXY_HEADERS=true` so rate limiting sees the real client IP. Railway works the same way. Free instances cold-start.

## Notes / limits

- Rate limiting and the retrieval cache are in-memory, per process. Run a single worker, or move them to Redis later.
- The curated source list (`knowledge/sources.py`) is deliberately small, and the pages are summarized by plain text extraction. Review and extend it before relying on it. The answers are general information, not legal advice.
