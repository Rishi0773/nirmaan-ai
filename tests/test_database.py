"""
NIRMAAN AI - Unit Tests: Database Repository & Schema
"""

import pytest
import sqlite3
from pathlib import Path
from src.database.connection import init_db, get_connection
from src.database.repository import Repository


@pytest.fixture
def temp_repo(tmp_path):
    test_db = tmp_path / "test_nirmaan.db"
    init_db(test_db)
    return Repository(test_db)


def test_user_creation_and_retrieval(temp_repo):
    uid = temp_repo.create_user("test_officer", "Test Officer", "Ward Officer", "officer@test.com", "9999999999", "Indiranagar")
    assert uid > 0

    user = temp_repo.get_user_by_username("test_officer")
    assert user is not None
    assert user["full_name"] == "Test Officer"
    assert user["role"] == "Ward Officer"


def test_report_lifecycle(temp_repo):
    rep_id = temp_repo.create_report(
        report_uid="REP-TEST-001",
        latitude=12.9352,
        longitude=77.6245,
        ward_name="Koramangala",
        waste_category="plastic",
        address="Test Road 5th Block",
        is_simulated=1
    )
    assert rep_id > 0

    report = temp_repo.get_report_by_id(rep_id)
    assert report is not None
    assert report["report_uid"] == "REP-TEST-001"
    assert report["status"] == "Pending"

    # Status update
    temp_repo.update_report_status(rep_id, "Under Cleanup")
    updated = temp_repo.get_report_by_id(rep_id)
    assert updated["status"] == "Under Cleanup"


def test_task_creation_and_status(temp_repo):
    rep_id = temp_repo.create_report(
        report_uid="REP-TEST-002",
        latitude=12.9719,
        longitude=77.6412,
        ward_name="Indiranagar",
        waste_category="hazardous"
    )
    task_id = temp_repo.create_task(
        task_code="TASK-TEST-002",
        report_id=rep_id,
        assigned_team="Team Bravo"
    )
    assert task_id > 0

    tasks = temp_repo.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0]["task_code"] == "TASK-TEST-002"

    # Synchronized report status
    rep = temp_repo.get_report_by_id(rep_id)
    assert rep["status"] == "Under Cleanup"
