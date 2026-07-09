"""
Tool: Suggest Follow-ups
Trigger: Topics/outcomes present and user asks for suggestions, or automatically after logging
Reads: Topics, outcomes from current state
Writes: suggested_followups[] array
"""

import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
from app.core.json_utils import extract_json


SUGGEST_FOLLOWUPS_PROMPT = """You are an AI assistant for pharmaceutical/life science field representatives. 
Based on the interaction details provided, suggest 3-5 specific, actionable follow-up actions.

Consider:
- The topics discussed and any products/treatments mentioned
- The HCP's sentiment (if negative, suggest addressing concerns)
- Standard pharma rep best practices (scheduling follow-ups, sharing materials, updating CRM)
- Any outcomes or agreements that need follow-through

Return ONLY a JSON array of follow-up strings. Each should be concise and actionable (under 60 chars).
No markdown, no explanations — just the JSON array.

Example output:
["Schedule follow-up meeting in 2 weeks", "Send OncoBoost Phase III PDF", "Add Dr. Sharma to advisory board invite list"]"""


async def suggest_followups(message: str, current_state: dict) -> dict:
    """
    Generate suggested follow-up actions based on the interaction context.
    """
    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0.7,  # Slightly higher for creative suggestions
    )

    # Build context from current form state
    context_parts = []
    if current_state.get("hcp_name"):
        context_parts.append(f"HCP: {current_state['hcp_name']}")
    if current_state.get("interaction_type"):
        context_parts.append(f"Type: {current_state['interaction_type']}")
    if current_state.get("topics_discussed"):
        context_parts.append(f"Topics: {current_state['topics_discussed']}")
    if current_state.get("outcomes"):
        context_parts.append(f"Outcomes: {current_state['outcomes']}")
    if current_state.get("sentiment"):
        context_parts.append(f"Sentiment: {current_state['sentiment']}")
    if current_state.get("materials_shared"):
        context_parts.append(f"Materials shared: {', '.join(current_state['materials_shared'])}")

    context = "\n".join(context_parts) if context_parts else "No interaction details available yet."

    messages = [
        SystemMessage(content=SUGGEST_FOLLOWUPS_PROMPT),
        HumanMessage(
            content=f"User message: {message}\n\nInteraction context:\n{context}"
        ),
    ]

    response = await llm.ainvoke(messages)
    content = response.content.strip()

    followups = extract_json(content)
    if not isinstance(followups, list):
        followups = [str(followups)] if followups else ["Schedule follow-up meeting", "Send relevant materials", "Update CRM notes"]

    # Ensure all items are strings
    followups = [str(f) for f in followups[:5]]

    return {
        "tool_used": "suggest_followups",
        "updated_state": {"suggested_followups": followups},
        "chat_reply": "💡 Here are my suggested follow-up actions:\n" +
                      "\n".join(f"  • {f}" for f in followups),
        "suggested_followups": followups,
    }
