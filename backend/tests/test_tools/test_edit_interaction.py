"""
Tests for the edit_interaction tool.
Verifies that corrections are parsed into partial updates.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json


@pytest.mark.asyncio
async def test_edit_interaction_returns_partial_update():
    """Tool should return only the changed fields."""
    mock_response = MagicMock()
    mock_response.content = json.dumps({"time": "15:00"})

    with patch("app.agents.tools.edit_interaction.ChatGroq") as MockGroq:
        instance = MockGroq.return_value
        instance.ainvoke = AsyncMock(return_value=mock_response)

        from app.agents.tools.edit_interaction import edit_interaction
        result = await edit_interaction(
            "Actually the time was 3pm not 2pm",
            {"hcp_name": "Dr. Smith", "time": "14:00", "sentiment": "Positive"}
        )

    assert result["tool_used"] == "edit_interaction"
    assert result["updated_state"]["time"] == "15:00"
    # Should NOT include unchanged fields
    assert "hcp_name" not in result["updated_state"]


@pytest.mark.asyncio
async def test_edit_interaction_handles_empty_changes():
    """Tool should handle when no changes could be parsed."""
    mock_response = MagicMock()
    mock_response.content = "I'm not sure what to change"

    with patch("app.agents.tools.edit_interaction.ChatGroq") as MockGroq:
        instance = MockGroq.return_value
        instance.ainvoke = AsyncMock(return_value=mock_response)

        from app.agents.tools.edit_interaction import edit_interaction
        result = await edit_interaction("blah blah", {})

    assert result["tool_used"] == "edit_interaction"
    assert result["updated_state"] == {}
    assert "couldn't understand" in result["chat_reply"].lower()


@pytest.mark.asyncio
async def test_edit_interaction_list_modification():
    """Tool should return the list modifications exactly as received from the model, without merging."""
    mock_response = MagicMock()
    mock_response.content = json.dumps({"attendees": ["Adarsh", "Amit"]})

    with patch("app.agents.tools.edit_interaction.ChatGroq") as MockGroq:
        instance = MockGroq.return_value
        instance.ainvoke = AsyncMock(return_value=mock_response)

        from app.agents.tools.edit_interaction import edit_interaction
        result = await edit_interaction(
            "attendees were only adarsh and amit",
            {"attendees": ["Person 1", "Person 2", "Amit", "Adarsh"]}
        )

    assert result["tool_used"] == "edit_interaction"
    assert result["updated_state"]["attendees"] == ["Adarsh", "Amit"]

