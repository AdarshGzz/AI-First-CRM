"""
Tests for the submit_to_db tool.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_submit_requires_hcp_name():
    """Submit should reject when HCP name is empty."""
    from app.agents.tools.submit_to_db import submit_to_db

    result = await submit_to_db("Submit this", {"hcp_name": "", "sentiment": "Positive"})

    assert result["tool_used"] == "submit_to_db"
    assert "required" in result["chat_reply"].lower() or "cannot" in result["chat_reply"].lower()
    assert result["updated_state"] == {}


@pytest.mark.asyncio
async def test_submit_requires_hcp_name_missing():
    """Submit should reject when current state has no hcp_name at all."""
    from app.agents.tools.submit_to_db import submit_to_db

    result = await submit_to_db("Save to database", {})

    assert result["tool_used"] == "submit_to_db"
    assert result["updated_state"] == {}
