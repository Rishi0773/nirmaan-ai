"""
NIRMAAN AI - Unit & Regression Tests for UI Redesign, Services, and Architecture
"""

import pytest
from pathlib import Path
from src.database.connection import init_db
from src.database.repository import Repository
from services.search_service import search_reports
from services.assistant_service import process_assistant_query
from services.report_service import validate_report_submission
from components.shared_ui import severity_badge, status_badge, render_clean_table
from components.hero import get_hero_background_style


def test_search_service_matches_uid_and_ward(tmp_path):
    test_db = tmp_path / "test_search.db"
    init_db(test_db)
    repo = Repository(test_db)

    # Insert test reports
    r1 = repo.create_report("REP-TEST-001", 12.9352, 77.6245, "Koramangala", "plastic", address="80 Feet Road")
    r2 = repo.create_report("REP-TEST-002", 12.9719, 77.6412, "Indiranagar", "organic", address="100 Feet Road")

    # Search by UID
    res_uid = search_reports("REP-TEST-001", repo)
    assert len(res_uid) == 1
    assert res_uid[0]["report_uid"] == "REP-TEST-001"

    # Search by ward
    res_ward = search_reports("Koramangala", repo)
    assert len(res_ward) == 1
    assert res_ward[0]["ward_name"] == "Koramangala"

    # Partial search
    res_part = search_reports("002", repo)
    assert len(res_part) == 1
    assert res_part[0]["report_uid"] == "REP-TEST-002"

    # Empty query returns empty list
    assert search_reports("", repo) == []
    assert search_reports("   ", repo) == []


def test_assistant_service_intents_and_report_tracking(tmp_path):
    test_db = tmp_path / "test_asst.db"
    init_db(test_db)
    repo = Repository(test_db)

    # Test how to report inquiry
    res_rep = process_assistant_query("How do I report a garbage hotspot?", repo)
    assert "Report Garbage" in res_rep["response"]
    assert res_rep["action"] == "navigate_report"

    # Test priority formula inquiry
    res_prio = process_assistant_query("How is cleanup priority calculated?", repo)
    assert "Score" in res_prio["response"]
    assert "0.35" in res_prio["response"]
    assert res_prio["action"] == "navigate_queue"

    # Test severity inquiry
    res_sev = process_assistant_query("What do severity levels mean?", repo)
    assert "LOW" in res_sev["response"]
    assert "HIGH" in res_sev["response"]

    # Test tracking specific existing report
    r = repo.create_report("REP-BLR-999", 12.9352, 77.6245, "Koramangala", "mixed_trash")
    repo.save_severity(r, "High", 85.0, 45.0, {})
    repo.save_priority_score(r, score=80.0, severity_comp=28.0, recurrence_comp=20.0, waste_type_comp=16.0, waiting_time_comp=16.0)

    res_track = process_assistant_query("Track REP-BLR-999", repo)
    assert "REP-BLR-999" in res_track["response"]
    assert "High" in res_track["response"]
    assert res_track["action"] == "view_dossier"


def test_report_validation_service():
    # Valid report in Bengaluru
    valid, err = validate_report_submission(12.9352, 77.6245, "Koramangala", "plastic", has_image=True)
    assert valid is True
    assert err is None

    # Missing image
    valid, err = validate_report_submission(12.9352, 77.6245, "Koramangala", "plastic", has_image=False)
    assert valid is False
    assert "photograph is required" in err

    # Out of bounds coordinates (Delhi)
    valid, err = validate_report_submission(28.6139, 77.2090, "Koramangala", "plastic", has_image=True)
    assert valid is False
    assert "outside Greater Bengaluru" in err

    # Invalid waste class
    valid, err = validate_report_submission(12.9352, 77.6245, "Koramangala", "nuclear_waste", has_image=True)
    assert valid is False
    assert "not recognized" in err


def test_hero_background_fallback():
    # Calling get_hero_background_style returns a valid CSS background string
    style = get_hero_background_style()
    assert "background:" in style
    assert "linear-gradient" in style


def test_badges_and_table_markup():
    # Severity badge
    h_badge = severity_badge("High")
    assert "badge-high" in h_badge
    assert "HIGH" in h_badge

    l_badge = severity_badge("Low")
    assert "badge-low" in l_badge
    assert "LOW" in l_badge

    # Status badge
    c_badge = status_badge("Cleared")
    assert "badge-cleared" in c_badge
    assert "CLEARED" in c_badge
