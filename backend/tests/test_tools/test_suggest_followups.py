"""
Tests for the suggest_followups tool.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json


@pytest.mark.asyncio
async def test_suggest_followups_returns_array():
    """Tool should return an array of follow-up suggestions."""
    mock_response = MagicMock()
    mock_response.content = json.dumps([
        "Schedule follow-up meeting in 2 weeks",
        "Send OncoBoost Phase III PDF",
        "Add Dr. Sharma to advisory board invite list",
    ])

    with patch("app.agents.tools.suggest_followups.ChatGroq") as MockGroq:
        instance = MockGroq.return_value
        instance.ainvoke = AsyncMock(return_value=mock_response)

        from app.agents.tools.suggest_followups import suggest_followups
        result = await suggest_followups(
            "What follow-ups should I do?",
            {"hcp_name": "Dr. Sharma", "topics_discussed": "OncoBoost trial"}
        )

    assert result["tool_used"] == "suggest_followups"
    assert isinstance(result["suggested_followups"], list)
    assert len(result["suggested_followups"]) >= 1
    assert result["updated_state"]["suggested_followups"] == result["suggested_followups"]
