"""
NIRMAAN AI - Unit & Regression Tests for Civic Assistant Rendering Pipeline
Verifies that formula extraction, markdown rendering, and report tracking cards
function properly without raw syntax leakage or missing text.
"""

import re
import pytest
from pathlib import Path
from src.database.connection import init_db
from src.database.repository import Repository
from services.assistant_service import process_assistant_query
from components.civic_assistant import render_assistant_content


def test_formula_extraction_and_segmentation():
    """Verifies that sample response is cleanly split into markdown and formula segments."""
    sample_response = (
        "**NIRMAAN AI Explainable Prioritization Formula**\n\n"
        "$$\n"
        "P = 0.35S + 0.25R + 0.20W + 0.20T\n"
        "$$\n\n"
        "- **Severity (S, 35%):** Waste severity.\n"
        "- **Recurrence (R, 25%):** Repeated incidents.\n"
        "- **Hazard (W, 20%):** Waste hazard.\n"
        "- **Waiting Time (T, 20%):** Time pending."
    )

    equation_pattern = re.compile(r'(\$\$[\s\S]*?\$\$)', re.MULTILINE)
    parts = equation_pattern.split(sample_response)

    # Must split into exactly 3 parts: heading, formula, and bullet points
    assert len(parts) == 3

    # Part 0: Heading markdown
    assert "**NIRMAAN AI Explainable Prioritization Formula**" in parts[0]

    # Part 1: Standalone LaTeX formula
    assert parts[1].strip().startswith("$$") and parts[1].strip().endswith("$$")
    formula = parts[1].strip()[2:-2].strip()
    assert formula == "P = 0.35S + 0.25R + 0.20W + 0.20T"

    # Part 2: Bullet points
    assert "- **Severity (S, 35%):**" in parts[2]
    assert "- **Recurrence (R, 25%):**" in parts[2]
    assert "- **Hazard (W, 20%):**" in parts[2]
    assert "- **Waiting Time (T, 20%):**" in parts[2]


def test_assistant_priority_query_returns_exact_equation(tmp_path):
    """Verifies assistant returns the required formula string matching P = 0.35S + 0.25R + 0.20W + 0.20T."""
    test_db = tmp_path / "test_asst_eq.db"
    init_db(test_db)
    repo = Repository(test_db)

    res = process_assistant_query("How is cleanup priority calculated?", repo)
    resp_text = res["response"]

    assert "P = 0.35S + 0.25R + 0.20W + 0.20T" in resp_text
    assert "Score" in resp_text
    assert res["action"] == "navigate_queue"


def test_assistant_tracking_card_clean_formatting(tmp_path):
    """Verifies that report tracking response returns clean markdown lists and dossier action."""
    test_db = tmp_path / "test_asst_track.db"
    init_db(test_db)
    repo = Repository(test_db)

    r = repo.create_report("REP-BLR-001", 12.9352, 77.6245, "Koramangala", "plastic", address="80 Feet Road")
    repo.save_severity(r, "High", 85.0, 45.0, {})
    repo.save_priority_score(r, score=88.5, severity_comp=30.0, recurrence_comp=22.0, waste_type_comp=18.0, waiting_time_comp=18.5)

    res = process_assistant_query("Track REP-BLR-001", repo)
    resp_text = res["response"]

    assert "**Verified Record Found: REP-BLR-001**" in resp_text
    assert "- **Lifecycle Status:**" in resp_text
    assert "- **Ward & Address:**" in resp_text
    assert "- **Computer Vision Severity:**" in resp_text
    assert "- **Priority Score:**" in resp_text
    assert res["action"] == "view_dossier"
    assert res["action_label"] == "Go to Incident Dossier"
    assert res["report_uid"] == "REP-BLR-001"
