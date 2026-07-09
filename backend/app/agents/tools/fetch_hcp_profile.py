"""
Tool: Fetch HCP Profile
Trigger: Doctor's name mentioned (e.g., "tell me about Dr. Sharma")
Reads: HCP name from message
Writes: Chat message with profile context (does NOT update the form)
"""

import json
# pyrefly: ignore [missing-import]
from sqlalchemy import select, func
from app.db.session import async_session_factory
from app.models.db_models import HCPProfileModel
from app.cache.redis_client import get_cache, set_cache


async def fetch_hcp_profile(message: str, current_state: dict) -> dict:
    """
    Look up an HCP profile from the database (with Redis cache).
    Returns profile info as a chat message — does not modify form state.
    """
    # Extract the doctor name from the message
    # Simple heuristic: look for "Dr." or "Doctor" followed by a name
    name_query = _extract_doctor_name(message)

    if not name_query:
        return {
            "tool_used": "fetch_hcp_profile",
            "updated_state": {},
            "chat_reply": "I couldn't identify a doctor's name in your message. "
                          "Try something like 'Tell me about Dr. Sharma'.",
            "suggested_followups": [],
        }

    # Check Redis cache first
    cache_key = f"hcp:{name_query.lower()}"
    cached = get_cache(cache_key)

    if cached:
        profile_data = json.loads(cached)
        return _format_profile_response(profile_data, from_cache=True)

    # Query database with fuzzy matching
    async with async_session_factory() as session:
        # Case-insensitive partial match
        result = await session.execute(
            select(HCPProfileModel).where(
                func.lower(HCPProfileModel.name).contains(name_query.lower())
            )
        )
        profile = result.scalar_one_or_none()

        if profile is None:
            return {
                "tool_used": "fetch_hcp_profile",
                "updated_state": {},
                "chat_reply": f"❌ No HCP profile found for '{name_query}'. "
                              f"Available profiles are in the system — try a different name.",
                "suggested_followups": [],
            }

        profile_data = {
            "id": profile.id,
            "name": profile.name,
            "specialty": profile.specialty,
            "tier": profile.tier,
            "last_interaction_sentiment": profile.last_interaction_sentiment,
            "notes": profile.notes,
        }

        # Cache for 5 minutes
        set_cache(cache_key, json.dumps(profile_data), expire_seconds=300)

        return _format_profile_response(profile_data, from_cache=False)


def _extract_doctor_name(message: str) -> str:
    """Extract a doctor's name from natural language."""
    message_lower = message.lower()

    # Common patterns
    for prefix in ["dr.", "dr ", "doctor ", "about dr.", "about dr ", "about doctor "]:
        idx = message_lower.find(prefix)
        if idx != -1:
            # Get the name after the prefix
            name_start = idx + len(prefix)
            remaining = message[name_start:].strip()
            # Take the first 1-3 words as the name
            words = remaining.split()
            name_words = []
            for word in words[:3]:
                # Stop at punctuation or common non-name words
                clean = word.strip(".,!?;:")
                if clean.lower() in ["and", "or", "the", "a", "for", "about", "what", "is", "to"]:
                    break
                if clean:
                    name_words.append(clean)
            if name_words:
                return " ".join(name_words)

    return ""


def _format_profile_response(profile_data: dict, from_cache: bool = False) -> dict:
    """Format an HCP profile into a chat response."""
    p = profile_data
    cache_note = " (cached)" if from_cache else ""

    reply_lines = [
        f"👤 **{p['name']}**{cache_note}",
        f"   🏥 Specialty: {p['specialty']}",
        f"   ⭐ Tier: {p['tier']}",
    ]

    if p.get("last_interaction_sentiment"):
        sentiment_emoji = {"Positive": "😊", "Neutral": "😐", "Negative": "😟"}.get(
            p["last_interaction_sentiment"], "❓"
        )
        reply_lines.append(f"   {sentiment_emoji} Last Sentiment: {p['last_interaction_sentiment']}")

    if p.get("notes"):
        reply_lines.append(f"   📝 Notes: {p['notes']}")

    return {
        "tool_used": "fetch_hcp_profile",
        "updated_state": {},  # HCP profile does NOT update the form
        "chat_reply": "\n".join(reply_lines),
        "suggested_followups": [],
    }
