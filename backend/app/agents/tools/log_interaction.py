"""
Tool: Log Interaction
Trigger: New meeting/interaction described in natural language.
Reads: Chat text
Writes: Full form JSON (all fields extracted from the message)
"""

import json
from datetime import date, timedelta
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
# pyrefly: ignore [missing-import]
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
from app.core.json_utils import extract_json


LOG_INTERACTION_PROMPT = """You are an AI assistant that extracts structured interaction data from natural language descriptions of HCP (Healthcare Professional) interactions.

Extract the following fields from the user's message. Return ONLY valid JSON, no other text:

{{
  "hcp_name": "Doctor's full name (e.g., Dr. Smith)",
  "interaction_type": "Meeting|Call|Email|Video Call|Conference",
  "date": "YYYY-MM-DD format or empty string if not mentioned",
  "time": "HH:MM format (24hr) or empty string if not mentioned",
  "attendees": ["list of attendee names mentioned, empty array if none"],
  "topics_discussed": "Summary of topics discussed",
  "materials_shared": ["list of materials/documents shared, empty array if none"],
  "samples_distributed": ["list of product samples given, empty array if none"],
  "sentiment": "Positive|Neutral|Negative based on the HCP's described reaction",
  "outcomes": "Key outcomes or agreements from the interaction",
  "follow_up_actions": "Any next steps or follow-up tasks mentioned"
}}

Rules:
- If a field is not mentioned, use reasonable defaults (empty string or empty array).
- For dates, resolve ALL relative references using today's date which is {today}:
  - "today" → {today}
  - "tomorrow" → {tomorrow}
  - "day after tomorrow" → {day_after_tomorrow}
  - "yesterday" → {yesterday}
  If no date is mentioned, leave it empty.
- For sentiment, infer from context clues like "positive", "receptive", "interested" → Positive, "concerned", "unhappy", "skeptical" → Negative, otherwise → Neutral.
- Return ONLY the JSON object, no markdown, no explanations."""


async def log_interaction(message: str, current_state: dict) -> dict:
    """
    Extract structured interaction data from a natural language message.
    Returns a dict with all form fields populated.
    """
    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0.1,
    )

    today = date.today()
    system_prompt = LOG_INTERACTION_PROMPT.format(
        today=today.isoformat(),
        tomorrow=(today + timedelta(days=1)).isoformat(),
        day_after_tomorrow=(today + timedelta(days=2)).isoformat(),
        yesterday=(today - timedelta(days=1)).isoformat(),
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Extract interaction data from this message:\n\n{message}"),
    ]

    response = await llm.ainvoke(messages)
    content = response.content.strip()

    extracted = extract_json(content)

    # Build the response with defaults for missing fields
    result = {
        "hcp_name": extracted.get("hcp_name", ""),
        "interaction_type": extracted.get("interaction_type", "Meeting"),
        "date": extracted.get("date", ""),
        "time": extracted.get("time", ""),
        "attendees": extracted.get("attendees", []),
        "topics_discussed": extracted.get("topics_discussed", ""),
        "materials_shared": extracted.get("materials_shared", []),
        "samples_distributed": extracted.get("samples_distributed", []),
        "sentiment": extracted.get("sentiment", "Neutral"),
        "outcomes": extracted.get("outcomes", ""),
        "follow_up_actions": extracted.get("follow_up_actions", ""),
        "suggested_followups": [],
    }

    return {
        "tool_used": "log_interaction",
        "updated_state": result,
        "chat_reply": f"✅ Logged interaction with {result['hcp_name'] or 'HCP'}. "
                      f"Type: {result['interaction_type']}, Sentiment: {result['sentiment']}. "
                      f"Review the form and let me know if anything needs correction.",
        "suggested_followups": [],
    }
