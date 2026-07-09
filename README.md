# AI-CRM Interaction Logger

AI-driven CRM interaction logger for life science field representatives. All data entry happens through natural language in the chat panel — the form is read-only and purely reflects Redux state.

![Architecture](docs/architecture.md)

## 🏗️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React + Redux Toolkit + Vite | Read-only form + AI chat panel |
| Backend | FastAPI + WebSocket | Message relay + rate limiting |
| Agent | LangGraph + Groq (gemma2-9b-it) | Intent routing + 5 tool nodes |
| Cache | Redis | Rate limiting + HCP profile cache |
| Database | Neon (serverless Postgres) | Interaction logs + HCP profiles |

## 📁 Project Structure

```
├── frontend/                 # React + Redux + Vite
│   └── src/
│       ├── app/store.js               # Redux store
│       ├── features/interaction/       # Slice + selectors
│       ├── components/FormPanel/       # Read-only form
│       ├── components/ChatPanel/       # AI chat assistant
│       └── api/chatApi.js             # WebSocket client
│
├── backend/                  # FastAPI + LangGraph
│   └── app/
│       ├── main.py                    # FastAPI entrypoint
│       ├── routers/chat_ws.py         # WebSocket endpoint
│       ├── services/                  # Agent service + rate limiter
│       ├── agents/                    # LangGraph graph + 5 tools
│       ├── models/                    # Pydantic + SQLAlchemy
│       ├── db/                        # Neon session + seed data
│       ├── cache/                     # Redis client
│       └── core/config.py            # Environment config
│
└── docs/                     # Architecture + agent design + demo
```

## 🚀 Quick Start

### Prerequisites
- Node.js ≥ 18
- Python ≥ 3.11
- Redis (local or cloud like Upstash)

### 1. Clone & Configure

```bash
cp .env.example .env
# Fill in your credentials:
#   GROQ_API_KEY    → https://console.groq.com
#   NEON_DATABASE_URL → https://neon.tech
#   REDIS_URL       → redis://localhost:6379/0
```

### 2. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

On startup, the backend will:
- Create database tables in Neon
- Seed 8 mock HCP profiles
- Open WebSocket at `ws://localhost:8000/ws/chat`

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — you'll see the split-screen CRM.

## 🤖 The 5 AI Tools

All triggered via natural language in the chat panel:

| # | Tool | Trigger Example |
|---|------|----------------|
| 1 | **Log Interaction** | "Met Dr. Smith today at 2pm, discussed Product X, positive sentiment" |
| 2 | **Edit Interaction** | "Actually the time was 3pm not 2pm" |
| 3 | **Suggest Follow-ups** | "What follow-ups should I do?" |
| 4 | **Fetch HCP Profile** | "Tell me about Dr. Sharma" |
| 5 | **Submit to Database** | "Save this interaction" |

## 🛡️ Rate Limiting

Redis-backed fixed-window counter protects the Groq free tier:
- Key: `rate:groq:{minute_bucket}`
- Default: 25 requests/minute
- Returns `rate_limited` with `retry_after_seconds` when exceeded

## 🔌 WebSocket API

**Client → Server:**
```json
{
  "message": "Met Dr. Smith today at 2pm...",
  "current_state": { "...redux form state..." }
}
```

**Server → Client (result):**
```json
{
  "type": "result",
  "tool_used": "log_interaction",
  "updated_state": { "hcp_name": "Dr. Smith", ... },
  "chat_reply": "✅ Logged interaction with Dr. Smith.",
  "suggested_followups": []
}
```

## 📝 Why Neon?

Serverless Postgres means no local DB setup — reviewers just need a connection string in `.env`. No Docker, no pg_dump, no migrations to run manually.

## 📄 License

MIT
