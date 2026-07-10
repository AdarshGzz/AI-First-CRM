"""
Tool: Edit Interaction
Trigger: Correction phrased (e.g., "actually it was 3pm not 2pm")
Reads: Chat text + current form state
Writes: Only the changed fields (partial update)
"""

import json
from datetime import date, timedelta
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
# pyrefly: ignore [missing-import]
from langchain_core.messages import HumanMessage, SystemMessage
# pyrefly: ignore [missing-import]
from app.core.config import settings
from app.core.json_utils import extract_json


EDIT_INTERACTION_PROMPT = """You are an AI assistant that interprets correction/edit requests for HCP interaction forms.

The user wants to modify some fields of an existing interaction log. You are given:
1. The correction message from the user
2. The current form state

For any list/array fields (like 'attendees', 'materials_shared', or 'samples_distributed'), if the user requests to add, remove, or modify elements, you MUST return the COMPLETE final list representing the desired updated state of that field. Do not just return the added/removed items.

Return ONLY the fields that need to change as a JSON object. Do not include fields that should remain the same.

Available fields:
- hcp_name (string)
- interaction_type ("Meeting"|"Call"|"Email"|"Video Call"|"Conference")
- date (YYYY-MM-DD)
- time (HH:MM, 24hr)
- attendees (array of strings)
- topics_discussed (string)
- materials_shared (array of strings)
- samples_distributed (array of strings)
- sentiment ("Positive"|"Neutral"|"Negative")
- outcomes (string)
- follow_up_actions (string)

Return ONLY valid JSON with the changed fields. No markdown, no explanations.

IMPORTANT: Today's date is {today}. When the user references relative dates, resolve them:
- "today" → {today}
- "tomorrow" → {tomorrow}
- "day after tomorrow" → {day_after_tomorrow}
- "yesterday" → {yesterday}

Examples:
- Current state: {{"time": "14:00"}}
  Message: "Actually the time was 3pm not 2pm"
  Response: {{"time": "15:00"}}

- Current state: {{"sentiment": "Neutral", "attendees": ["Dr. Smith"]}}
  Message: "Change sentiment to positive and add Dr. Jones as attendee"
  Response: {{"sentiment": "Positive", "attendees": ["Dr. Smith", "Dr. Jones"]}}

- Current state: {{"attendees": ["Person A", "Person B", "Person C"]}}
  Message: "remove Person B and Person C"
  Response: {{"attendees": ["Person A"]}}

- Current state: {{"attendees": ["Person A", "Person B"]}}
  Message: "delete all attendees"
  Response: {{"attendees": []}}"""


async def edit_interaction(message: str, current_state: dict) -> dict:
    """
    Parse a correction message and return only the fields that need updating.
    """
    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0.1,
    )

    current_state_str = json.dumps(current_state, indent=2, default=str)

    today = date.today()
    system_prompt = EDIT_INTERACTION_PROMPT.format(
        today=today.isoformat(),
        tomorrow=(today + timedelta(days=1)).isoformat(),
        day_after_tomorrow=(today + timedelta(days=2)).isoformat(),
        yesterday=(today - timedelta(days=1)).isoformat(),
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=f"Current form state:\n{current_state_str}\n\n"
                    f"User's correction:\n{message}"
        ),
    ]

    response = await llm.ainvoke(messages)
    content = response.content.strip()

    changes = extract_json(content)

    if not changes:
        return {
            "tool_used": "edit_interaction",
            "updated_state": {},
            "chat_reply": "I couldn't understand what to change. Could you be more specific? "
                          "For example: 'Change the time to 3pm' or 'Set sentiment to positive'.",
            "suggested_followups": [],
        }



    # Build a human-readable summary of changes
    change_descriptions = []
    for field, value in changes.items():
        field_label = field.replace("_", " ").title()
        if isinstance(value, list):
            value_str = ", ".join(value) if value else "none"
        else:
            value_str = str(value)
        change_descriptions.append(f"**{field_label}** → {value_str}")

    change_summary = ", ".join(change_descriptions)

    return {
        "tool_used": "edit_interaction",
        "updated_state": changes,
        "chat_reply": f"✏️ Updated: {change_summary}. Let me know if anything else needs correction.",
        "suggested_followups": [],
    }
