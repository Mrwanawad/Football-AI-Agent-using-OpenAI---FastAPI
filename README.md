<p align="center">
  <h1 align="center">AI Agent Platform</h1>
  <p align="center">
    A RESTful API backend for creating, managing, and chatting with AI agents — via <strong>text and voice</strong>.
    <br />
    Built with <strong>FastAPI</strong> &middot; <strong>SQLAlchemy</strong> &middot; <strong>OpenAI</strong>
  </p>
</p>

<p align="center">
  <a href="#features">Features</a> &nbsp;&bull;&nbsp;
  <a href="#tech-stack">Tech Stack</a> &nbsp;&bull;&nbsp;
  <a href="#quick-start">Quick Start</a> &nbsp;&bull;&nbsp;
  <a href="#api-reference">API Reference</a> &nbsp;&bull;&nbsp;
  <a href="#testing">Testing</a> &nbsp;&bull;&nbsp;
  <a href="#docker">Docker</a> &nbsp;&bull;&nbsp;
  <a href="#kubernetes">Kubernetes</a> &nbsp;&bull;&nbsp;
  <a href="#configuration">Configuration</a> &nbsp;&bull;&nbsp;
  <a href="#project-structure">Project Structure</a>
</p>

---

## Features

- **Agent Management** — Create AI agents with custom system prompts, then update or delete them at any time.
- **Multi-Session Chat** — Each agent supports multiple independent chat sessions with full conversation history.
- **Text Messaging** — Send messages and receive context-aware responses powered by OpenAI GPT.
- **Voice Interaction** — Upload audio, get it transcribed (Whisper STT), processed by GPT, and returned as speech (TTS) — all in a single request.
- **JWT Authentication** — Secure OAuth2 password flow with Argon2 password hashing.
- **Ownership Authorization** — Users can only access their own agents, sessions, and messages.
- **Interactive API Docs** — Auto-generated Swagger UI and ReDoc.
- **Dockerized** — Single-command containerized deployment with built-in health checks.
- **Kubernetes Ready** — Production-grade K8s manifests with auto-scaling, persistent storage, and Ingress.
- **Fully Tested** — Unit and integration tests with mocked OpenAI calls — no API key needed to run tests.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) 0.111 |
| **Server** | [Uvicorn](https://www.uvicorn.org/) (ASGI) |
| **Database** | SQLite via [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (ORM) |
| **Validation** | [Pydantic v2](https://docs.pydantic.dev/) |
| **AI** | [OpenAI API](https://platform.openai.com/) — GPT-4o-mini, Whisper, TTS |
| **Auth** | JWT (python-jose) + Argon2 (passlib) |
| **Testing** | pytest, pytest-asyncio, unittest.mock |
| **Containerization** | Docker (Python 3.11-slim) |
| **Orchestration** | Kubernetes (Deployment, Service, Ingress, HPA) |

---

## Quick Start

### Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/ai-agent-platform.git
cd ai-agent-platform
```

### 2. Create environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```env
OPENAI_API_KEY=sk-...
SECRET_KEY=your-long-random-secret
```

### 3. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

The API is now live at **http://localhost:8000**.

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/token` | Login and receive a JWT |

> All endpoints below require the header: `Authorization: Bearer <token>`

### Agents

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/agents` | Create an agent with a custom system prompt |
| `GET` | `/api/v1/agents` | List all your agents |
| `GET` | `/api/v1/agents/{id}` | Get a single agent |
| `PATCH` | `/api/v1/agents/{id}` | Update agent name or prompt |
| `DELETE` | `/api/v1/agents/{id}` | Delete agent and all its data |

### Sessions

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/agents/{id}/sessions` | Start a new chat session |
| `GET` | `/api/v1/agents/{id}/sessions` | List sessions for an agent |
| `GET` | `/api/v1/agents/{id}/sessions/{sid}` | Get session with full message history |
| `DELETE` | `/api/v1/agents/{id}/sessions/{sid}` | Delete a session and its messages |

### Messaging

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/agents/{id}/sessions/{sid}/messages` | Send a text message |
| `POST` | `/api/v1/agents/{id}/sessions/{sid}/voice` | Send audio and receive audio response |

### Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok", "version": "1.0.0"}` |

<details>
<summary><strong>Example: Text Message</strong></summary>

**Request:**
```json
POST /api/v1/agents/1/sessions/1/messages
{
  "content": "Hello, how are you?"
}
```

**Response:**
```json
{
  "user_message": {
    "id": 1,
    "session_id": 1,
    "role": "user",
    "content": "Hello, how are you?",
    "created_at": "2025-01-01T00:00:00Z"
  },
  "agent_message": {
    "id": 2,
    "session_id": 1,
    "role": "assistant",
    "content": "I'm doing great! How can I help you today?",
    "created_at": "2025-01-01T00:00:01Z"
  }
}
```
</details>

<details>
<summary><strong>Example: Voice Message</strong></summary>

**Request:**
```
POST /api/v1/agents/1/sessions/1/voice
Content-Type: multipart/form-data

audio: <file.webm>
```

**Response:**
```
Content-Type: audio/mpeg
Body: <binary audio data>
```

The voice endpoint performs the full pipeline in a single call:

`Audio upload → Speech-to-Text (Whisper) → GPT Response → Text-to-Speech → Audio response`

Both the transcribed user message and the agent reply are saved to the session history.
</details>

---

## Testing

Tests run against an in-memory SQLite database with fully mocked OpenAI calls — **no API key or network access required**.

```bash
# Run all tests
pytest -v

# Run with coverage report
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
```

**Test suite includes:**
- User registration and authentication
- Agent CRUD operations and ownership authorization
- Session lifecycle management
- Text messaging with multi-turn conversation history
- Voice interaction (STT → Chat → TTS pipeline)
- OpenAI service integration (mocked)

---

## Docker

```bash
# Build the image
docker build -t ai-agent-platform .

# Run the container
docker run -p 8000:8000 --env-file .env ai-agent-platform
```

The container runs as a **non-root user** and includes a built-in **health check** that pings `/health` every 30 seconds.

---

## Kubernetes

Production-ready Kubernetes manifests are provided in the `k8s/` directory.

```
k8s/
├── namespace.yaml      # Dedicated namespace
├── secret.yaml         # API keys (OPENAI_API_KEY, SECRET_KEY)
├── configmap.yaml      # Non-sensitive configuration
├── deployment.yaml     # 2 replicas, rolling updates, health probes
├── service.yaml        # ClusterIP service (port 80 → 8000)
├── ingress.yaml        # Nginx Ingress with audio upload & timeout support
├── pvc.yaml            # 1Gi persistent volume for SQLite data
└── hpa.yaml            # Auto-scaling (2–10 pods, CPU/memory based)
```

### Deploy to a cluster

```bash
# 1. Edit secrets with your real keys
kubectl apply -f k8s/namespace.yaml
kubectl -n ai-agent-platform create secret generic ai-agent-platform-secret \
  --from-literal=OPENAI_API_KEY="sk-..." \
  --from-literal=SECRET_KEY="your-secret"

# 2. Apply all manifests
kubectl apply -f k8s/

# 3. Verify
kubectl -n ai-agent-platform get all
```

### What's included

| Manifest | Purpose |
|---|---|
| **Deployment** | Rolling updates with zero downtime, liveness & readiness probes on `/health`, resource limits (256–512 Mi) |
| **Service** | ClusterIP routing — internal traffic on port 80 forwarded to container port 8000 |
| **Ingress** | External access via Nginx Ingress with increased body size (10 MB for audio uploads) and read/send timeouts (120s for OpenAI calls) |
| **HPA** | Horizontal Pod Autoscaler scales from 2 to 10 replicas based on CPU (70%) and memory (80%) utilization |
| **PVC** | Persistent storage for the SQLite database so data survives pod restarts |
| **ConfigMap** | All non-sensitive env vars (model names, DB URL, token expiry, etc.) |
| **Secret** | Sensitive values — for production, use [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) or an external secret manager |

> **Note**: Update the `host` field in `k8s/ingress.yaml` to match your domain. Uncomment the `tls` block to enable HTTPS.

---

## Configuration

All settings can be overridden via environment variables or a `.env` file.

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | **(Required)** Your OpenAI API key |
| `SECRET_KEY` | — | **(Required in prod)** JWT signing secret |
| `DATABASE_URL` | `sqlite:///./ai_agent_platform.db` | Database connection string |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Chat completion model |
| `OPENAI_TTS_MODEL` | `tts-1` | Text-to-speech model |
| `OPENAI_TTS_VOICE` | `alloy` | TTS voice (`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`) |
| `OPENAI_STT_MODEL` | `whisper-1` | Speech-to-text model |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | JWT token lifetime (default: 24 hours) |

---

## Project Structure

```
ai-agent-platform/
├── app/
│   ├── api/
│   │   ├── router.py                  # Aggregates all endpoint routers
│   │   └── v1/endpoints/
│   │       ├── auth.py                # Register & login
│   │       ├── agents.py             # Agent CRUD
│   │       └── sessions.py           # Sessions, text & voice messaging
│   ├── core/
│   │   ├── config.py                  # App settings & environment config
│   │   └── security.py               # JWT creation/validation, password hashing
│   ├── db/
│   │   └── database.py               # SQLAlchemy engine, session factory, Base
│   ├── models/                        # SQLAlchemy ORM models
│   │   ├── user.py                    # User
│   │   ├── agent.py                   # Agent (with system prompt)
│   │   ├── session.py                 # ChatSession
│   │   └── message.py                # Message (user/assistant)
│   ├── schemas/                       # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── agent.py
│   │   └── session.py
│   ├── services/                      # Business logic layer
│   │   ├── user_service.py            # Registration, authentication
│   │   ├── agent_service.py           # Agent CRUD logic
│   │   ├── chat_service.py            # Session & messaging orchestration
│   │   └── openai_service.py          # OpenAI API wrapper (async)
│   └── tests/
│       ├── test_chat.py               # Session & messaging integration tests
│       └── test_services.py           # Service layer unit tests
├── k8s/                                # Kubernetes manifests
│   ├── namespace.yaml
│   ├── secret.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── pvc.yaml
│   └── hpa.yaml
├── main.py                             # FastAPI app factory & startup
├── Dockerfile                          # Production container
├── requirements.txt                    # Pinned Python dependencies
├── pyproject.toml                      # Project metadata
├── postman_collection.json             # Postman API collection
└── .env.example                        # Environment template
```

---

## Database Schema

```
┌──────────┐       ┌──────────┐       ┌───────────────┐       ┌──────────┐
│  users   │1─────*│  agents  │1─────*│ chat_sessions │1─────*│ messages │
├──────────┤       ├──────────┤       ├───────────────┤       ├──────────┤
│ id       │       │ id       │       │ id            │       │ id       │
│ username │       │ name     │       │ title         │       │ session_id│
│ email    │       │ prompt   │       │ agent_id (FK) │       │ role     │
│ password │       │ owner_id │       │ user_id  (FK) │       │ content  │
│ is_active│       │ created  │       │ created_at    │       │ created  │
│ created  │       │ updated  │       └───────────────┘       └──────────┘
└──────────┘       └──────────┘
```

All deletions cascade: deleting a user removes their agents, sessions, and messages.

---

## Postman Collection

Import `postman_collection.json` into [Postman](https://www.postman.com/) for a ready-to-use API test suite with automatic variable extraction.

**Recommended flow:**
1. **Register** — creates your account
2. **Login** — JWT token is auto-saved to `{{token}}`
3. **Create Agent** — agent ID auto-saved to `{{agent_id}}`
4. **Create Session** — session ID auto-saved to `{{session_id}}`
5. **Send Text Message** or **Send Voice Message**

---

## License

This project is open source and available under the [MIT License](LICENSE).
