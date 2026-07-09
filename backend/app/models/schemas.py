"""
Pydantic schemas — the single source of truth for data contracts
between the LangGraph agent and FastAPI WebSocket responses.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time
from enum import Enum


# ── Enums ────────────────────────────────────────────────────

class InteractionType(str, Enum):
    MEETING = "Meeting"
    CALL = "Call"
    EMAIL = "Email"
    VIDEO_CALL = "Video Call"
    CONFERENCE = "Conference"


class Sentiment(str, Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"


# ── Form State (Redux mirror) ───────────────────────────────

class InteractionForm(BaseModel):
    """Mirrors the Redux interaction state exactly."""
    hcp_name: Optional[str] = ""
    interaction_type: Optional[InteractionType] = InteractionType.MEETING
    date: Optional[str] = ""  # ISO date string
    time: Optional[str] = ""  # HH:MM string
    attendees: list[str] = Field(default_factory=list)
    topics_discussed: Optional[str] = ""
    materials_shared: list[str] = Field(default_factory=list)
    samples_distributed: list[str] = Field(default_factory=list)
    sentiment: Optional[Sentiment] = Sentiment.NEUTRAL
    outcomes: Optional[str] = ""
    follow_up_actions: Optional[str] = ""
    suggested_followups: list[str] = Field(default_factory=list)


# ── WebSocket Messages ──────────────────────────────────────

class WSIncomingMessage(BaseModel):
    """Client → Server over WebSocket."""
    message: str
    current_state: dict = Field(default_factory=dict)


class WSTokenMessage(BaseModel):
    """Server → Client: streamed LLM token."""
    type: str = "token"
    content: str = ""


class WSResultMessage(BaseModel):
    """Server → Client: final tool result."""
    type: str = "result"
    tool_used: str = ""
    updated_state: dict = Field(default_factory=dict)
    chat_reply: str = ""
    suggested_followups: list[str] = Field(default_factory=list)


class WSRateLimitMessage(BaseModel):
    """Server → Client: rate limit hit."""
    type: str = "rate_limited"
    retry_after_seconds: int = 10


class WSErrorMessage(BaseModel):
    """Server → Client: error."""
    type: str = "error"
    message: str = ""


# ── HCP Profile ─────────────────────────────────────────────

class HCPProfile(BaseModel):
    """HCP profile data returned by fetch_hcp_profile tool."""
    id: Optional[int] = None
    name: str = ""
    specialty: str = ""
    tier: str = ""
    last_interaction_sentiment: Optional[str] = None
    notes: Optional[str] = None
