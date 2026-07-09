"""
Tests for the fetch_hcp_profile tool.
"""

import pytest
from app.agents.tools.fetch_hcp_profile import _extract_doctor_name


def test_extract_doctor_name_with_dr_prefix():
    assert _extract_doctor_name("Tell me about Dr. Sharma") == "Sharma"


def test_extract_doctor_name_with_doctor_prefix():
    assert _extract_doctor_name("Who is Doctor Smith?") == "Smith"


def test_extract_doctor_name_with_full_name():
    name = _extract_doctor_name("Look up Dr. Priya Sharma")
    assert "Priya" in name or "Sharma" in name


def test_extract_doctor_name_no_match():
    assert _extract_doctor_name("What is the weather today?") == ""


def test_extract_doctor_name_with_about():
    assert _extract_doctor_name("about Dr. Patel") == "Patel"
