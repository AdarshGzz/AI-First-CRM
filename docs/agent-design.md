# Agent Design

## LangGraph Graph Structure

The agent is a stateful graph with a **router node** and **5 tool nodes**. The router classifies user intent via Groq, then conditional edges route execution to the appropriate tool.

```
[User message + current state]
        │
        ▼
   [Router Node] ── Groq classifies intent
        │
   ┌────┼────────────┬────────────┬────────────┐
   ▼    ▼            ▼            ▼            ▼
[Log]  [Edit]  [Suggest]  [Fetch HCP]  [Submit]
   │    │            │            │            │
   └────┴────────────┴────────────┴────────────┘
        │
   [Pydantic Validation]
        │
   [Return JSON to FastAPI]
```

## Agent State

```python
class AgentState(TypedDict):
    messages: list[BaseMessage]     # Chat history for current turn
    current_form_state: dict        # Redux state from frontend
    intent: str                     # Classified intent
    tool_output: dict               # Validated payload to return
```

## Router Logic

The router node sends the user's message + current form state to Groq for intent classification. Context matters:
- Empty form + meeting description → `log_interaction`
- Populated form + correction → `edit_interaction`
- Doctor name + "about"/"who" → `fetch_hcp_profile`
- "Next steps"/"follow-ups" → `suggest_followups`
- "Save"/"submit"/"finalize" → `submit_to_db`

## Tool Details

### 1. Log Interaction
- **Trigger**: New meeting/interaction described
- **Process**: Groq extracts structured fields from natural language
- **Output**: Full form JSON (all fields)

### 2. Edit Interaction
- **Trigger**: Correction or change to existing data
- **Process**: Groq identifies changed fields, returns partial update
- **Output**: Only changed fields (merged client-side)

### 3. Suggest Follow-ups
- **Trigger**: Asks for next steps or explicitly requests
- **Process**: Groq analyzes topics/outcomes/sentiment
- **Output**: Array of 3-5 actionable follow-up strings

### 4. Fetch HCP Profile
- **Trigger**: Doctor name mentioned with lookup intent
- **Process**: Query Neon (Redis-cached) for profile
- **Output**: Chat message only (does NOT modify form)

### 5. Submit to Database
- **Trigger**: Save/submit/finalize phrasing
- **Process**: Validate form state, insert into Neon
- **Output**: Confirmation with record ID

## Why This Design?

- **One Groq call for routing** + **one for tool execution** = 2 LLM calls per turn (predictable cost)
- **Pydantic validation** on every tool output = no malformed state reaches Redux
- **Redis cache on HCP lookups** = repeated doctor queries don't hit Neon or Groq
