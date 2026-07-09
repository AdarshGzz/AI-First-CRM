# Demo Script

## Duration: 10-15 minutes

---

## 1. Architecture Overview (1-2 min)

- Show the HLD diagram from `docs/architecture.md`
- Highlight: React ↔ WebSocket ↔ FastAPI ↔ LangGraph ↔ Groq + Neon + Redis
- Emphasize: "All data entry through chat — form is read-only"

## 2. Repo & Folder Structure Tour (1 min)

- Walk through the monorepo structure
- Point out the layered backend: `routers/` → `services/` → `agents/`
- Note: one file per tool under `agents/tools/`
- Mention: `models/schemas.py` as single source of truth

## 3. Live Demo (6-8 min)

### Tool 1: Log Interaction
```
Type: "Met Dr. Priya Sharma today at 2pm for a meeting, discussed OncoBoost Phase III trial results, she was very positive about the efficacy data, shared the clinical brochure"
```
- Watch the form populate automatically
- Point out: HCP name, type, date/time, topics, sentiment all extracted

### Tool 2: Edit Interaction
```
Type: "Actually the meeting was at 3pm not 2pm, and change sentiment to neutral"
```
- Watch only the time and sentiment fields update
- Highlight: partial update, not full replacement

### Tool 3: Fetch HCP Profile
```
Type: "Tell me about Dr. Sharma"
```
- Watch the profile appear in chat (not the form)
- Note: cached in Redis for subsequent lookups

### Tool 4: Suggest Follow-ups
```
Type: "What follow-ups should I do?"
```
- Watch the suggested follow-ups appear in the form
- Highlight: context-aware suggestions based on topics/sentiment

### Tool 5: Submit to Database
```
Type: "Submit this interaction"
```
- Watch the confirmation with record ID
- Verify in Neon dashboard that the row exists

## 4. Code Walkthrough (2-3 min)

- **Router node**: `agents/graph.py` — show the intent classification prompt
- **One tool file**: `agents/tools/log_interaction.py` — show the extraction prompt
- **Pydantic schema**: `models/schemas.py` — show `InteractionForm` and `WSResultMessage`
- **Rate limiter**: `services/rate_limiter.py` — show Redis INCR pattern

## 5. Closing (1 min)

- Summarize the architectural challenge: "How do you make a form that's entirely AI-driven?"
- Answer: "Strict contracts (Pydantic), single reducer pattern (Redux), and a router that never lets unvalidated data through"
- Mention: no local DB setup needed (Neon), rate limiting protects free tier (Redis)
