# Architecture

## High-Level Architecture

```
React (Form panel | Chat panel)
        │  WS  { message, current_state }
        ▼
FastAPI backend  ──── rate-limit check ────▶  Redis (counter)
        │                                        (reject/queue if over budget)
        ▼
LangGraph agent (router node)
        │
   ┌────┼─────────────────────┐
   ▼    ▼                     ▼
Groq LLM   Neon Postgres   (5 tool nodes execute here)
(extraction,  (read/write,
 stream=True)  cached via Redis
               for HCP lookups)
        │
        ▼
Validated JSON state → FastAPI → WS relay → Redux → Form re-renders
```

## Component Responsibilities

### Frontend
- **React + Redux Toolkit**: Form fields are `readOnly`, driven entirely by Redux state
- **WebSocket client**: Sends `{message, current_state}`, receives streamed tokens + final result
- **Single reducer pattern**: `state = {...state, ...action.payload.updated_state}` — one action type handles all 5 tools

### Backend
- **FastAPI**: WebSocket bridge between React and LangGraph
- **Rate Limiter**: Redis INCR + EXPIRE pattern, checked before every Groq call
- **Agent Service**: Invokes compiled LangGraph graph, formats response

### Agent (LangGraph)
- **Router Node**: Groq classifies intent → routes to 1 of 5 tool nodes
- **Tool Nodes**: Each tool extracts/processes data, returns validated Pydantic output
- **State**: TypedDict carrying messages, form state, intent, and tool output

### Data Layer
- **Neon Postgres**: `interactions` + `hcp_profiles` tables via SQLAlchemy async
- **Redis**: Rate limiting counters + HCP profile cache (5-min TTL)

## Why This Layering?

1. `routers/` never imports LangGraph directly — only `services/` does
2. One file per tool under `agents/tools/` — trivially locatable by reviewers
3. `models/schemas.py` is the single source of truth for JSON contracts
4. `services/rate_limiter.py` sits between WS router and agent — one gate, not five

## Data Flow

1. Rep types message in chat panel
2. React sends `{message, current_state}` over WebSocket
3. FastAPI checks Redis rate counter
4. If allowed → invoke LangGraph graph
5. Router node asks Groq to classify intent
6. Appropriate tool node executes (may query Neon or Groq)
7. Pydantic-validated result sent back over WebSocket
8. Redux merges `updated_state` → form re-renders
