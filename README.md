# 🧬 AI-First CRM: Life Sciences Interaction Logger

An advanced, AI-driven CRM interaction logging system designed specifically for **Life Science Field Representatives**. By implementing an **AI-First UX**, all data entry is processed through natural language conversation in a chat panel. The CRM form itself is read-only and serves as a direct, reactive reflection of the Redux state updated in real-time by the AI agent.

---

## 🏗️ Architecture Overview

The system is designed with a decoupled, reactive monorepo architecture:

```
                  ┌──────────────────────────────────────────┐
                  │          React Frontend Client           │
                  │ (Read-only Form UI & Interactive Chat)   │
                  └────────────────────┬─────────────────────┘
                                       │ WebSocket Connection
                                       │ { message, current_form_state }
                                       ▼
                  ┌──────────────────────────────────────────┐
                  │             FastAPI Backend              │
                  │ (ASGI Web Server & WebSocket Controller) │
                  └────────────────────┬─────────────────────┘
                                       │
                        Check Rate Limit via Redis
                        (INCR + EXPIRE Bucket)
                                       │
                                       ▼
                  ┌──────────────────────────────────────────┐
                  │             LangGraph Agent              │
                  │  (Intent Router & State Orchestration)   │
                  └───────┬──────────────────────────┬───────┘
                          │                          │
                 Query / Extract              Fetch / Commit
                          ▼                          ▼
               ┌─────────────────────┐    ┌─────────────────────┐
               │    Groq Cloud API   │    │    Neon Serverless  │
               │ (llama-3.3-70b-v /  │    │     PostgreSQL      │
               │   gemma2-9b-it)     │    └──────────┬──────────┘
               └─────────────────────┘               │
                                              Cached Profile Lookup
                                                     ▼
                                          ┌─────────────────────┐
                                          │    Upstash Redis    │
                                          │    (5-Min Cache)    │
                                          └─────────────────────┘
```

---

## 🚀 Key Features

*   **Chat-First CRM Data Entry**: Reps describe interactions in natural language (e.g., *"Met Dr. Sharma, discussed OncoBoost, positive sentiment"*), and the AI automatically extracts, structures, and updates the form.
*   **Context-Aware Intent Classification**: A central LangGraph **Router Node** classifies user messages to determine which specialized tool should handle the request.
*   **Granular Delta Updates (Smart Edits)**: Modifications (e.g., *"Actually it was 3pm not 2pm"*) update only the relevant fields in Redux using partial state patches, avoiding state corruption or resetting other fields.
*   **High Performance HCP Lookups**: Integrates an Upstash Redis cache (5-minute TTL) for Healthcare Professional (HCP) profiles, ensuring repeated lookup queries avoid hitting Neon Postgres.
*   **Enterprise-Grade Rate Limiting**: Protects LLM token budgets (Groq API) using a Redis-backed fixed-window rate limiter checked directly at the WebSocket layer.
*   **Strict Pydantic Schema Contracts**: Unvalidated JSON is never merged into the frontend state. All payloads are validated using Pydantic on the server side prior to delivery.

---

## 📁 Repository Directory Structure

```
├── frontend/                     # React + Redux Toolkit + Vite
│   ├── src/
│   │   ├── app/
│   │   │   └── store.js          # Global Redux store configuration
│   │   ├── features/
│   │   │   └── interaction/
│   │   │       ├── interactionSlice.js     # Redux slice with state-merging logic
│   │   │       └── interactionSelectors.js # Reselect selectors for form inputs
│   │   ├── components/
│   │   │   ├── ChatPanel/        # Chat interface with streamed token display
│   │   │   │   ├── ChatInput.jsx
│   │   │   │   ├── ChatMessage.jsx
│   │   │   │   └── ChatPanel.jsx
│   │   │   └── FormPanel/        # Form inputs displaying current state (read-only)
│   │   │       ├── FormPanel.jsx
│   │   │       └── fields/       # Modular input field components (Attendees, Outcomes, etc.)
│   │   ├── api/
│   │   │   └── chatApi.js        # Reconnecting WebSocket client instance
│   │   ├── App.jsx               # Layout setup (split screen form/chat)
│   │   └── index.css             # Vanilla CSS UI design system
│   └── package.json
│
├── backend/                      # FastAPI Web Framework & LangGraph Agent
│   ├── app/
│   │   ├── main.py               # Application entrypoint & lifespan lifecycle hooks
│   │   ├── core/
│   │   │   └── config.py         # Pydantic Settings configuration & env parsing
│   │   ├── db/
│   │   │   ├── session.py        # Neon SQLAlchemy database connection & session setup
│   │   │   └── seed.py           # Auto-seeding script for 8 mock HCP profiles
│   │   ├── cache/
│   │   │   └── redis_client.py   # Upstash Redis client with TTL caching helpers
│   │   ├── models/
│   │   │   ├── db_models.py      # SQLAlchemy ORM schemas (interactions, hcp_profiles)
│   │   │   └── schemas.py        # Pydantic validation models (WebSocket messaging, Forms)
│   │   ├── routers/
│   │   │   └── chat_ws.py        # Real-time WebSocket router & stream handler
│   │   ├── services/
│   │   │   ├── agent_service.py  # Wrapper service invoking the LangGraph agent
│   │   │   └── rate_limiter.py   # Redis-backed fixed-window rate limiter
│   │   └── agents/
│   │       ├── graph.py          # LangGraph structure, Router edge, & model setup
│   │       ├── state.py          # TypedDict defining internal agent workflow state
│   │       └── tools/            # Monolithic agent action nodes
│   │           ├── log_interaction.py    # Extracts structured form from text description
│   │           ├── edit_interaction.py   # Merges deltas and edits existing form fields
│   │           ├── suggest_followups.py  # Generates actionable clinical next-steps
│   │           ├── fetch_hcp_profile.py  # Queries HCP profile (Neon DB with Redis cache)
│   │           └── submit_to_db.py       # Commits final state to interactions table
│   ├── requirements.txt
│   └── .env.example
│
└── docs/                         # Additional Design & Walkthrough Documentation
    ├── architecture.md           # Component layout & WebSocket flow details
    ├── agent-design.md           # Graph node-edge routing & LLM context patterns
    └── demo-script.md            # Live walkthrough script with copy-paste prompts
```

---

## 🤖 The 5 Agent Tools in Detail

All tools are automatically routed and executed depending on natural language instructions:

| # | Tool Node Name | Intent Trigger Examples | Action Taken | Output Payload |
|---|----------------|-------------------------|--------------|----------------|
| 1 | `log_interaction` | *"Met Dr. Priya Sharma today at 2:00 PM, discussed OncoBoost"* | Groq extracts structural fields using Pydantic JSON structure extraction. | Populates empty fields in form. |
| 2 | `edit_interaction` | *"Actually it was 3:00 PM not 2:00 PM"* or *"Change sentiment to neutral"* | Identifies changes to make relative to current form fields, outputs patch. | Partial state update (merges with current form). |
| 3 | `suggest_followups` | *"What follow-ups should I do?"* or *"Give me next steps"* | Analyzes clinical topics/sentiment to output context-rich next actions. | Appends suggested follow-ups list. |
| 4 | `fetch_hcp_profile` | *"Tell me about Dr. Sharma"* or *"Who is Rajesh Patel?"* | Queries Upstash Redis cache; falls back to Neon Postgres DB, caching results for 5 min. | Sends profile details to chat panel (leaves form unmodified). |
| 5 | `submit_to_db` | *"Save this interaction"* or *"Finalize and submit"* | Inserts current form data into Neon database using SQLAlchemy. | Returns a success message with DB insertion ID, resets form. |

---

## 🛠️ Local Environment Setup

### 1. Configure Environment Variables
Copy `.env.example` to `.env` in the root (or `backend/` / `frontend/` directory) and populate your credentials:

```bash
# ── Groq API (LLM) ──────────────────────────────────────
GROQ_API_KEY=your-groq-api-key       # Get from https://console.groq.com
GROQ_MODEL=llama-3.3-70b-versatile  # Recommended model

# ── Neon Serverless Postgres ────────────────────────────
NEON_DATABASE_URL=your-neon-postgres-connection-string

# ── Upstash Redis (REST) ────────────────────────────────
REDIS_URL=https://your-upstash-redis-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-upstash-token

# ── Rate Limiting ───────────────────────────────────────
RATE_LIMIT_MAX_REQUESTS=25
RATE_LIMIT_WINDOW_SECONDS=60
```

### 2. Backend Setup & Run
The backend requires **Python 3.11+**.

```bash
# Move to backend folder
cd backend

# Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package dependencies
pip install -r requirements.txt

# Run the FastAPI server via Uvicorn
uvicorn app.main:app --reload --port 8000
```

On server start, the backend will automatically:
1. Initialize the tables in Neon Postgres (`interactions`, `hcp_profiles`).
2. Seeding script executes to inject 8 default mock doctors into the database.
3. Open a WebSocket channel listening on `ws://localhost:8000/ws/chat`.

### 3. Frontend Setup & Run
The frontend requires **Node.js 18+**.

```bash
# Move to frontend folder
cd frontend

# Install client packages
npm install

# Run the local Vite dev server
npm run dev
```

*   **Application Interface**: Open `http://localhost:5173` to interact with the split-screen CRM dashboard.
*   **Websocket Routing**: Frontend links to WebSocket server. By default, it connects to local port `8000` or falls back to production Azure deployment endpoint if configured in environments.

---

## ⚡ Technical Details & Design Decisions

### 1. Redis Caching for HCP Lookup
To minimize DB overhead and Groq API calls during frequent reference checks, the `fetch_hcp_profile` tool checks Upstash Redis with:
*   Key: `hcp:profile:{hcp_name}`
*   TTL: **5 minutes** (300 seconds).
*   If a cache hit occurs, profile data is returned instantly. If a cache miss occurs, SQL queries Neon Postgres and updates Redis.

### 2. Fixed-Window Rate Limiter
The FastAPI socket router handles incoming payloads by passing them through the rate limiting service before calling LangGraph.
*   Key pattern: `rate:groq:{minute_timestamp_bucket}`
*   Limits requests per user to 25 requests per minute bucket.
*   If rate limit is breached, it yields a payload type `"rate_limited"` causing the frontend to display a cool-off warning stating the remaining cooldown seconds.

### 3. State Syncing Contract (Redux Merge)
The CRM form state is read-only. Updates are dispatched directly inside the [interactionSlice.js](frontend/src/features/interaction/interactionSlice.js):
```javascript
// Handles partial or full merges driven by agent Pydantic responses
state.form = {
  ...state.form,
  ...action.payload.updated_state
};
```
No frontend logic is computed in isolation — the AI-Agent maintains state coherence at all times.

---

## 📝 Demo Walkthrough Script

Follow these steps to demonstrate the full application capacity:

1.  **Log Interaction**: In the chat panel, type:
    > *"Met Dr. Priya Sharma today at 2:00 PM for a detailed meeting. We discussed OncoBoost Phase III trial results. She was very positive about the efficacy data. Shared the clinical brochure."*
    *   *Result*: The form elements instantly render with the extracted details (date, time, attendees, discussed topics, sentiment, shared materials).
2.  **Edit Interaction**: Type:
    > *"Actually, the meeting was at 3:00 PM, and sentiment was neutral."*
    *   *Result*: Only the time and sentiment fields update without overriding the rest of the form.
3.  **HCP Lookup**: Type:
    > *"Tell me about Dr. Sharma."*
    *   *Result*: The doctor's professional specialty, advisory status, and prior notes are retrieved (via Cache/Postgres) and shown in the chat window. The form remains untouched.
4.  **Suggest Follow-ups**: Type:
    > *"What follow-ups should I do?"*
    *   *Result*: Structured action items populate the bottom-most list of the CRM form panel.
5.  **Submit to DB**: Type:
    > *"Submit this interaction."*
    *   *Result*: Form state is stored as a row in the `interactions` database table. The form clears, and the agent returns a confirmation containing the generated record ID.

---

## 📄 License
Licensed under the [MIT License](LICENSE).
