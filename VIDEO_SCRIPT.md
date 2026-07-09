# Video Script: AI-CRM Interaction Logger Walkthrough

This document contains a comprehensive, 10–15 minute video presentation script and code flow walkthrough. It is structured into clear phases to cover the frontend walkthrough, live tool demonstrations, code architecture, and project understanding.

---

## 🎬 Video Overview

- **Estimated Duration:** 10–15 minutes.
- **Pacing:** Moderate, clear, and tutorial-like.
- **Target Audience:** Technical reviewers / project stakeholders.

---

## 📌 Phase 1: Project Goals & Task Understanding
**Visual:** Show the running application on screen (`http://localhost:5173`). Have a slide or a markdown document open representing the project goals, then switch back to the empty app interface.

---

### 🎙️ Script

> "Hello everyone! In this video, I will walk you through the **AI-CRM Interaction Logger**—a specialized tool designed for pharmaceutical and life science field representatives.
> 
> Let's start with a brief summary of **what I understood from this task and its requirements**.
> 
> As a field sales representative, logging interactions with Healthcare Professionals (HCPs) is critical for regulatory compliance and business intelligence. However, traditional CRM interfaces are notoriously tedious, requiring reps to manually navigate drop-downs, type out attendees, select dates, and fill in multi-step forms on their phones or laptops after a busy clinic visit.
> 
> The core goal of this project is to build an **AI-first CRM logging system**. Instead of the user typing into forms, they interact using natural language or voice transcription via a chat interface. 
>
> The key architectural requirements are:
> 1. A split-screen layout where the form is strictly **read-only** and bound directly to the frontend Redux state.
> 2. A real-time **WebSocket connection** for streaming chat tokens and tool results.
> 3. An intelligent **LangGraph-based backend agent** that determines the user's intent and executes specific tools.
> 4. Performance optimizations, including **Redis-backed rate limiting** to prevent API abuse, and **Redis-based caching** for HCP profiles.
> 5. A persistent database to save logged interactions and query doctor profiles, utilizing a serverless **PostgreSQL (Neon)** database.
>
> Now, let's walk through the frontend user interface."

---

## 📌 Phase 2: Frontend Walkthrough
**Visual:** Hover and click on key UI elements of the running web app. Show the split screen: the left Form panel and the right Chat panel. Highlight the "Connected" indicator.

---

### 🎙️ Script

> "Let's take a look at the user interface. It is divided into two distinct panels:
> 
> - **The Form Panel (Left):** This panel displays all the structured data fields for logging an interaction. These include the doctor's name, the date and time of the meeting, the attendees, topics discussed, materials shared, samples distributed, sentiment analysis, outcomes, and follow-up actions. 
>   - *Crucially*, all these input fields and text areas are **read-only**. You cannot click inside them and type. The only way to modify this form is by interacting with our AI assistant on the right. This ensures that the state remains clean and is purely driven by the Redux store.
> 
> - **The Chat Panel (Right):** This is the interactive console. It displays the connection status indicator at the top right (green for 'connected'). The chat feed shows the logs and responses, and the text area at the bottom lets the user describe interactions, make edits, query profiles, and submit the final form.
>
> The frontend uses **Redux Toolkit** to manage state, ensuring that any state updates sent by our backend WebSocket server instantly re-render the corresponding form field with zero delay."

---

## 📌 Phase 3: Live Demo of All 5 LangGraph Tools
**Visual:** Show the browser window. You will type 5 sequential inputs in the chat panel, showing how each tool is triggered and what happens on the left form panel.

---

### 🎙️ Script

> "Now, let's do a live demonstration of all **5 LangGraph tools** working properly in real-time. I will walk through the entire workflow of logging a meeting from scratch.
> 
> ### Tool 1: Log Interaction
> First, I will describe the meeting I had. I will write a simple summary of the conversation."

---

**Visual (Action):** Type in the chat box:
`"Had a great meeting with Dr. Smith today at 3pm. We discussed Product X efficacy, and the sentiment was positive."` and press **Enter**.
*Wait 1-2 seconds.* Watch the "Thinking..." loader appear, then see the Form update.

---

### 🎙️ Script

> "Our router correctly identified the **Log Interaction** intent. 
> 
> Notice how the form instantly updated:
> - **HCP Name:** `Dr. Smith`
> - **Date:** Automatically defaulted to today's date (`2024-02-26` or the current date).
> - **Time:** Set to `15:00` (parsing '3pm').
> - **Topics Discussed:** `Product X efficacy`.
> - **Sentiment:** Set to `Positive`.
> 
> The backend tool returned a clean JSON representation of these fields, and the UI synchronized immediately.
> 
> ### Tool 2: Edit Interaction
> Now, what if we made a mistake or want to modify something? Let's correct the time and add some attendees. I will type:
> `"Actually the time was 4pm, and I met Dr. Smith, Person A, and Person B."`"

---

**Visual (Action):** Type:
`"Actually the time was 4pm, and I met Dr. Smith, Person A, and Person B."` and press **Enter**.
Show the Time update to `16:00` and the Attendees list populate with `Dr. Smith`, `Person A`, and `Person B`.

---

### 🎙️ Script

> "The agent classified this as **Edit Interaction**. It updated the time to `16:00` and populated the attendees.
> 
> Now let's test a more complex edit—removing attendees. Previously, there was a bug where the backend always appended new attendees. We modified the LLM instructions so it returns the complete desired list state instead. Let's see this in action by typing:
> `"Wait, delete all attendees except Person A."`"

---

**Visual (Action):** Type:
`"Wait, delete all attendees except Person A."` and press **Enter**.
Show the Attendees list update to contain **only** `Person A`.

---

### 🎙️ Script

> "Excellent! The tool successfully replaced the entire attendee list with just `Person A`. The delete and modify operations for lists now work flawlessly.
> 
> ### Tool 3: Suggest Follow-ups
> Next, let's ask the assistant for suggested next steps based on the discussion topic of Product X. I will type:
> `"What should my next steps be?"`"

---

**Visual (Action):** Type:
`"What should my next steps be?"` and press **Enter**.
Show the yellow "AI Suggested Follow-ups" box appear under Follow-up Actions with 3 bulleted recommendations.

---

### 🎙️ Script

> "This triggers the **Suggest Follow-ups** tool. The LLM analyzed our context and generated 3 highly actionable, domain-specific tasks.
> 
> Notice how these items are fully interactive. If I click on '+ Schedule next meeting', it is appended to the main read-only 'Follow-up Actions' text area, and it is automatically removed from the suggested list. This makes follow-up logging fast and intuitive."

---

**Visual (Action):** Click the first suggested follow-up. Show it appearing in the 'Follow-up Actions' textarea. Click the second one and show it appending on a new line.

---

### 🎙️ Script

> "### Tool 4: Fetch HCP Profile
> Representatives often need to look up a doctor's background or preferences during a call. Let's ask about a doctor. I will type:
> `"Can you tell me about Dr. Sharma?"`"

---

**Visual (Action):** Type:
`"Can you tell me about Dr. Sharma?"` and press **Enter**.
Show the chat assistant display the doctor's details (Specialty, hospital, prescription patterns).

---

### 🎙️ Script

> "This triggers the **Fetch HCP Profile** tool. The agent queries our Neon Postgres database for the profile of Dr. Sharma and caches the result in Redis. The assistant then returns a neat summary of their profile, prescribing habits, and preferences, helping the representative prepare.
> 
> ### Tool 5: Submit to Database
> Now that our interaction details, sentiment, and follow-ups are perfectly logged on the left, we are ready to submit this log to the database. I will type:
> `"Submit this interaction to the database."`"

---

**Visual (Action):** Type:
`"Submit this interaction to the database."` and press **Enter**.
Show the success chat reply: `"Interaction logged successfully in Neon DB."`

---

### 🎙️ Script

> "This triggers our final tool, **Submit to Database**. It validates the active Redux state against our Pydantic database schema, sends it to Neon PostgreSQL via SQLAlchemy, and resets the form state so the rep is ready for their next meeting.
> 
> All 5 tools are fully functional and integrate smoothly together."

---

## 📌 Phase 4: Codebase & Architecture Walkthrough
**Visual:** Switch to VS Code. Show the project structure.

---

### 🎙️ Script

> "Now, let's do a simple walkthrough of our codebase structure and explain how the system operates under the hood.
> 
> ### Frontend Architecture
> In the `frontend/src/` folder:
> - **Redux Store ([app/store.js](file:///Users/adarshgzz/Desktop/Assignment/frontend/src/app/store.js))** defines our main state. The interaction slice ([features/interaction/interactionSlice.js](file:///Users/adarshgzz/Desktop/Assignment/frontend/src/features/interaction/interactionSlice.js)) handles the current form state, including `hcp_name`, `sentiment`, `attendees`, and `follow_up_actions`.
> - **API Module ([api/chatApi.js](file:///Users/adarshgzz/Desktop/Assignment/frontend/src/api/chatApi.js))** implements a robust WebSocket client. It manages the connection lifecycle, reconnect attempts, and routes incoming JSON messages to Redux.
> - **Components**: The split screen is managed by [FormPanel.jsx](file:///Users/adarshgzz/Desktop/Assignment/frontend/src/components/FormPanel/FormPanel.jsx) (which displays the read-only fields) and [ChatPanel.jsx](file:///Users/adarshgzz/Desktop/Assignment/frontend/src/components/ChatPanel/ChatPanel.jsx) (which binds to the socket and renders chat bubbles).
> 
> ### Backend Architecture & Code Flow
> Moving to the `backend/` directory:
> 1. **WebSocket Handler ([app/routers/chat_ws.py](file:///Users/adarshgzz/Desktop/Assignment/backend/app/routers/chat_ws.py)):** The WebSocket router accepts client messages. For each message, it calls [services/rate_limiter.py](file:///Users/adarshgzz/Desktop/Assignment/backend/app/services/rate_limiter.py) to check a Redis-backed fixed-window counter. If the rate limit is exceeded, it responds with a rate-limiting message.
> 2. **Agent Service ([app/services/agent_service.py](file:///Users/adarshgzz/Desktop/Assignment/backend/app/services/agent_service.py)):** This acts as the bridge between FastAPI and our LangGraph workflow. It creates an initial agent state and invokes the graph asynchronously.
> 3. **LangGraph Definition ([app/agents/graph.py](file:///Users/adarshgzz/Desktop/Assignment/backend/app/agents/graph.py)):** This is the heart of the backend. It constructs a state graph with a `router` node and conditional edges.
>    - The `router` node uses a Groq LLM to classify the user's prompt into one of the 5 intents.
>    - The graph routes execution to the corresponding node in `backend/app/agents/tools/`.
> 4. **Database & Caching Models:**
>    - [models/db_models.py](file:///Users/adarshgzz/Desktop/Assignment/backend/app/models/db_models.py) defines the SQLAlchemy models for Neon Postgres.
>    - When profiles are queried in `fetch_hcp_profile.py`, they are fetched from Redis cache first; if not found, it falls back to Neon Postgres and caches the result.
> 
> Let's look at the specific fix we made in [edit_interaction.py](file:///Users/adarshgzz/Desktop/Assignment/backend/app/agents/tools/edit_interaction.py)."

---

**Visual:** Open [edit_interaction.py](file:///Users/adarshgzz/Desktop/Assignment/backend/app/agents/tools/edit_interaction.py) in VS Code. Highlight the prompt changes and show that the merging code block has been removed.

---

### 🎙️ Script

> "Here in `edit_interaction.py`, we removed the hardcoded python merging block. We added instructions and structured examples directly into the `EDIT_INTERACTION_PROMPT` to guide the language model on how to handle list operations. Now, the LLM evaluates the correction message against the current state and returns the complete final list. This allows full support for adding, removing, and clearing list items.
>
> We also updated [FollowUpField.jsx](file:///Users/adarshgzz/Desktop/Assignment/frontend/src/components/FormPanel/fields/FollowUpField.jsx) in the frontend to make the suggested follow-ups interactive, dynamically updating Redux and removing the selected suggestions."

---

## 📌 Phase 5: Outro
**Visual:** Go back to the web application browser window showing the empty, reset form.

---

### 🎙️ Script

> "This architecture provides an extremely responsive, reactive, and robust CRM tool:
> - **Redux** acts as our single source of truth.
> - **FastAPI and WebSockets** handle low-latency communication.
> - **LangGraph** provides structured, reliable LLM reasoning.
> - **Redis and Neon Postgres** combine to deliver fast caching and reliable serverless storage.
> 
> Thank you so much for watching this walkthrough of the AI-CRM Interaction Logger!"

---
