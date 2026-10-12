"""
NIRMAAN AI - Unit Tests: Transparent Prioritization Scoring Engine
"""

import pytest
from datetime import datetime, timedelta
from src.engine.priority import compute_priority_score


def test_priority_score_computation():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # High severity, chronic recurrence, hazardous waste, pending for 5 days
    res = compute_priority_score(
        severity_score=95.0,
        recurrence_score=85.0,
        waste_category="hazardous",
        created_at_str=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
    )

    assert res["final_score"] >= 80.0
    assert "CRITICAL" in res["recommended_action"]
    assert res["contributions"]["severity_contrib"] > 0
    assert res["contributions"]["recurrence_contrib"] > 0


def test_priority_score_low_incident():
    res = compute_priority_score(
        severity_score=20.0,
        recurrence_score=15.0,
        waste_category="paper",
        created_at_str=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    assert res["final_score"] < 40.0
    assert "LOW" in res["recommended_action"]
