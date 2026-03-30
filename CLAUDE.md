# AI Agent Platform

FastAPI backend for creating and managing AI agents with text and voice interaction, using OpenAI APIs.

## Tech Stack

- **Python 3.13** / **FastAPI** / **Uvicorn**
- **SQLAlchemy 2.0** (SQLite) / **Pydantic v2**
- **OpenAI** (GPT-4o-mini, Whisper, TTS)
- **JWT auth** (OAuth2 password flow)
- **uv** for dependency management

## Project Structure

```
app/
├── api/v1/endpoints/   # Route handlers (auth, agents, sessions)
├── core/               # Config (settings) and security (JWT)
├── db/                 # SQLAlchemy engine + session
├── models/             # ORM models (User, Agent, ChatSession, Message)
├── schemas/            # Pydantic request/response schemas
├── services/           # Business logic (user, agent, chat, openai)
└── tests/              # pytest suite
main.py                 # App factory + lifespan
```

## Common Commands

```bash
# Run dev server
uvicorn main:app --reload

# Run tests (no API key needed — OpenAI is mocked)
pytest -v

# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Install dependencies
uv sync
# or
pip install -r requirements.txt

# Docker
docker build -t ai-agent-platform .
docker run -p 8000:8000 --env-file .env ai-agent-platform
```

## Key Patterns

- **Service layer**: Endpoints are thin — business logic lives in `app/services/`.
- **Async OpenAI**: All AI calls use `AsyncOpenAI` for non-blocking I/O.
- **Auth flow**: Register → Login (get JWT) → use `Authorization: Bearer <token>` header.
- **API prefix**: All routes under `/api/v1/`.
- **Tests**: Use in-memory SQLite DB and mocked OpenAI client. Run offline, no API costs.

## Environment Variables

Set via `.env` file (see `.env.example` in README):
- `OPENAI_API_KEY` — required
- `SECRET_KEY` — required in production
- `DATABASE_URL` — defaults to `sqlite:///./ai_agent_platform.db`
