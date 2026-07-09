"""
Tests for the log_interaction tool.
Verifies that structured data is correctly extracted from natural language.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json


@pytest.mark.asyncio
async def test_log_interaction_returns_correct_structure():
    """Tool output should match the expected response contract."""
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "hcp_name": "Dr. Smith",
        "interaction_type": "Meeting",
        "date": "2025-04-19",
        "time": "14:00",
        "attendees": [],
        "topics_discussed": "Product X efficacy",
        "materials_shared": [],
        "samples_distributed": [],
        "sentiment": "Positive",
        "outcomes": "Positive reception",
        "follow_up_actions": "",
    })

    with patch("app.agents.tools.log_interaction.ChatGroq") as MockGroq:
        instance = MockGroq.return_value
        instance.ainvoke = AsyncMock(return_value=mock_response)

        from app.agents.tools.log_interaction import log_interaction
        result = await log_interaction(
            "Met Dr. Smith today at 2pm, discussed Product X, he was positive",
            {}
        )

    assert result["tool_used"] == "log_interaction"
    assert "updated_state" in result
    assert "chat_reply" in result
    assert result["updated_state"]["hcp_name"] == "Dr. Smith"
    assert result["updated_state"]["sentiment"] == "Positive"


@pytest.mark.asyncio
async def test_log_interaction_handles_empty_response():
    """Tool should handle when LLM returns empty or malformed JSON."""
    mock_response = MagicMock()
    mock_response.content = "{}"

    with patch("app.agents.tools.log_interaction.ChatGroq") as MockGroq:
        instance = MockGroq.return_value
        instance.ainvoke = AsyncMock(return_value=mock_response)

        from app.agents.tools.log_interaction import log_interaction
        result = await log_interaction("Some message", {})

    assert result["tool_used"] == "log_interaction"
    assert result["updated_state"]["hcp_name"] == ""
    assert result["updated_state"]["interaction_type"] == "Meeting"
