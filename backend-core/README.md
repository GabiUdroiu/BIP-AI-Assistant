.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload



# Backend Core (Python / FastAPI)

Voice + chat API: speech-to-text, RAG-grounded chat replies, persistent conversation memory.

## Layout

```
app/
  core/config.py            settings (env-driven via pydantic-settings)
  models/                    request/response DTOs (Pydantic), generic ApiResponse<T>
  services/
    speech_service.py        offline speech-to-text (faster-whisper)
    rag_service.py            keyword-overlap retrieval over knowledge/*.md
    prompt_service.py         loads static system prompt/rules from prompts/
    conversation_service.py   chat history persistence (Postgres)
    chat_providers/           OpenRouter + Groq, one shared interface
  db/                         SQLAlchemy models + session (Neon Postgres)
  api/routes/                 HTTP controllers, one file per domain
  api/deps.py                 dependency-injected singletons
  main.py                     FastAPI app + router registration

knowledge/    RAG facts (retrieved per-query)
prompts/      static system prompt / behavior rules (always included)
```

## Setup

```bash
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your own keys:
- `OPENROUTER_API_KEY` — required for chat replies
- `GROQ_API_KEY` — optional, alternate provider (pass `"provider": "groq"` in `/api/chat` to use it)
- `DATABASE_URL` — Postgres connection string, for persistent chat memory

## Run

```bash
.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

First run of `/api/voice/process` downloads the `tiny.en` Whisper model automatically (public, no key).

## Endpoints

- `POST /api/voice/process` — audio file in, transcript out
- `POST /api/chat` — `{"message": str, "session_id"?: str, "provider"?: "openrouter"|"groq"}` → grounded, remembered reply
