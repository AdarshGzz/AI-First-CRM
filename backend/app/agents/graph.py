"""
LangGraph graph definition.
Router node classifies intent via Groq, then conditional edges route to 1 of 5 tool nodes.
"""

import json
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.agents.state import AgentState
from app.agents.tools.log_interaction import log_interaction
from app.agents.tools.edit_interaction import edit_interaction
from app.agents.tools.suggest_followups import suggest_followups
from app.agents.tools.fetch_hcp_profile import fetch_hcp_profile
from app.agents.tools.submit_to_db import submit_to_db
from app.core.config import settings


# ── Intent classification prompt ─────────────────────────────

ROUTER_PROMPT = """You are an intent classifier for an HCP (Healthcare Professional) interaction CRM system.
Given the user's message and the current form state, classify the intent into exactly ONE of these categories:

1. "log_interaction" — The user is describing a NEW interaction/meeting (e.g., "Met Dr. Smith today at 2pm, discussed Product X")
2. "edit_interaction" — The user wants to CORRECT or CHANGE an existing field (e.g., "actually it was 3pm", "change sentiment to positive")
3. "suggest_followups" — The user is asking for suggested next steps or follow-up actions (e.g., "what should I do next?", "suggest follow-ups")
4. "fetch_hcp_profile" — The user wants to look up a doctor's profile (e.g., "tell me about Dr. Sharma", "who is Dr. Patel?")
5. "submit_to_db" — The user wants to save/finalize the interaction (e.g., "submit this", "save to database", "finalize")

Context rules:
- If the form state is mostly empty and the user describes a meeting/call, it's "log_interaction"
- If the form state already has data and the user makes a correction, it's "edit_interaction"
- If the user mentions a doctor by name with "about", "who is", "profile", "tell me about" → "fetch_hcp_profile"
- If the user asks about next steps, recommendations, or follow-ups → "suggest_followups"
- If the user says save, submit, finalize, done, complete → "submit_to_db"

Return ONLY the intent string, nothing else. No quotes, no explanation."""


# ── Node functions ───────────────────────────────────────────

async def router_node(state: AgentState) -> dict:
    """Classify the user's intent using Groq LLM."""
    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0.0,
    )

    # Get the last user message
    user_message = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_message = msg.content
            break

    form_state = state.get("current_form_state", {})
    form_state_str = json.dumps(form_state, indent=2, default=str) if form_state else "{}"

    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(
            content=f"Current form state:\n{form_state_str}\n\nUser message: {user_message}"
        ),
    ]

    response = await llm.ainvoke(messages)
    intent = response.content.strip().lower().replace('"', '').replace("'", "")

    # Validate intent
    valid_intents = [
        "log_interaction", "edit_interaction", "suggest_followups",
        "fetch_hcp_profile", "submit_to_db"
    ]

    if intent not in valid_intents:
        # Default to log_interaction if we can't classify
        intent = "log_interaction"

    return {"intent": intent}


async def log_interaction_node(state: AgentState) -> dict:
    """Execute the log_interaction tool."""
    user_message = _get_last_user_message(state)
    result = await log_interaction(user_message, state.get("current_form_state", {}))
    return {
        "tool_output": result,
        "messages": [AIMessage(content=result["chat_reply"])],
    }


async def edit_interaction_node(state: AgentState) -> dict:
    """Execute the edit_interaction tool."""
    user_message = _get_last_user_message(state)
    result = await edit_interaction(user_message, state.get("current_form_state", {}))
    return {
        "tool_output": result,
        "messages": [AIMessage(content=result["chat_reply"])],
    }


async def suggest_followups_node(state: AgentState) -> dict:
    """Execute the suggest_followups tool."""
    user_message = _get_last_user_message(state)
    result = await suggest_followups(user_message, state.get("current_form_state", {}))
    return {
        "tool_output": result,
        "messages": [AIMessage(content=result["chat_reply"])],
    }


async def fetch_hcp_profile_node(state: AgentState) -> dict:
    """Execute the fetch_hcp_profile tool."""
    user_message = _get_last_user_message(state)
    result = await fetch_hcp_profile(user_message, state.get("current_form_state", {}))
    return {
        "tool_output": result,
        "messages": [AIMessage(content=result["chat_reply"])],
    }


async def submit_to_db_node(state: AgentState) -> dict:
    """Execute the submit_to_db tool."""
    user_message = _get_last_user_message(state)
    result = await submit_to_db(user_message, state.get("current_form_state", {}))
    return {
        "tool_output": result,
        "messages": [AIMessage(content=result["chat_reply"])],
    }


# ── Helper ───────────────────────────────────────────────────

def _get_last_user_message(state: AgentState) -> str:
    """Extract the last user message from state."""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""


# ── Routing function ─────────────────────────────────────────

def route_by_intent(state: AgentState) -> str:
    """Return the next node name based on classified intent."""
    return state.get("intent", "log_interaction")


# ── Graph construction ───────────────────────────────────────

def build_graph() -> StateGraph:
    """Build and compile the LangGraph agent graph."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("log_interaction", log_interaction_node)
    graph.add_node("edit_interaction", edit_interaction_node)
    graph.add_node("suggest_followups", suggest_followups_node)
    graph.add_node("fetch_hcp_profile", fetch_hcp_profile_node)
    graph.add_node("submit_to_db", submit_to_db_node)

    # Set entry point
    graph.set_entry_point("router")

    # Conditional edges from router to tool nodes
    graph.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "log_interaction": "log_interaction",
            "edit_interaction": "edit_interaction",
            "suggest_followups": "suggest_followups",
            "fetch_hcp_profile": "fetch_hcp_profile",
            "submit_to_db": "submit_to_db",
        },
    )

    # All tool nodes end the graph
    graph.add_edge("log_interaction", END)
    graph.add_edge("edit_interaction", END)
    graph.add_edge("suggest_followups", END)
    graph.add_edge("fetch_hcp_profile", END)
    graph.add_edge("submit_to_db", END)

    return graph.compile()


# Compiled graph singleton
agent_graph = build_graph()
