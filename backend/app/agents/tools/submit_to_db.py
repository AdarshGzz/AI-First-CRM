"""
Tool: Submit to Database
Trigger: "Save", "submit", "finalize" phrasing
Reads: Full current form state
Writes: DB row in interactions table + confirmation message
"""

from app.db.session import async_session_factory
from app.models.db_models import Interaction


async def submit_to_db(message: str, current_state: dict) -> dict:
    """
    Validate the current form state and persist it to the interactions table.
    """
    # Validate that we have minimum required fields
    hcp_name = current_state.get("hcp_name", "").strip()

    if not hcp_name:
        return {
            "tool_used": "submit_to_db",
            "updated_state": {},
            "chat_reply": "⚠️ Cannot submit: HCP Name is required. "
                          "Please log an interaction first (e.g., 'Met Dr. Smith today...').",
            "suggested_followups": [],
        }

    # Create the interaction record
    interaction = Interaction(
        hcp_name=hcp_name,
        interaction_type=current_state.get("interaction_type", "Meeting"),
        date=current_state.get("date", ""),
        time=current_state.get("time", ""),
        attendees=current_state.get("attendees", []),
        topics_discussed=current_state.get("topics_discussed", ""),
        materials_shared=current_state.get("materials_shared", []),
        samples_distributed=current_state.get("samples_distributed", []),
        sentiment=current_state.get("sentiment", "Neutral"),
        outcomes=current_state.get("outcomes", ""),
        follow_up_actions=current_state.get("follow_up_actions", ""),
    )

    try:
        async with async_session_factory() as session:
            session.add(interaction)
            await session.commit()
            await session.refresh(interaction)

            return {
                "tool_used": "submit_to_db",
                "updated_state": {},
                "chat_reply": f"✅ Interaction #{interaction.id} saved to database!\n"
                              f"   HCP: {hcp_name}\n"
                              f"   Type: {interaction.interaction_type}\n"
                              f"   Sentiment: {interaction.sentiment}\n\n"
                              f"You can start a new interaction or continue editing this one.",
                "suggested_followups": [],
            }

    except Exception as e:
        return {
            "tool_used": "submit_to_db",
            "updated_state": {},
            "chat_reply": f"❌ Failed to save interaction: {str(e)}. Please try again.",
            "suggested_followups": [],
        }
