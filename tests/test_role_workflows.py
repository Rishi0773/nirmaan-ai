"""
NIRMAAN AI - Unit Tests: Role-Based Workflows, Lifecycle State Transitions,
RBAC Enforcement, and Municipal Report Generation.
"""

import pytest
from pathlib import Path
from src.database.connection import init_db
from src.database.repository import Repository
from src.auth.rbac import has_permission, enforce_permission, ROLE_PERMISSIONS
from src.utils.reporting import (
    generate_incident_pdf_report,
    generate_ward_operations_pdf_report,
    generate_executive_pdf_report,
    export_reports_to_csv
)
from services.assistant_service import process_assistant_query


@pytest.fixture
def temp_repo(tmp_path):
    test_db = tmp_path / "test_roles_nirmaan.db"
    init_db(test_db)
    return Repository(test_db)


def test_rbac_permission_matrix():
    """Verify role permission boundaries as per municipal governance requirements."""
    # Cleanup Worker should NOT have approval or calibration rights
    worker = {"role": "Cleanup Worker", "id": 5, "username": "worker_01"}
    assert has_permission("accept_task", worker) is True
    assert has_permission("report_blocked", worker) is True
    assert has_permission("submit_verification", worker) is True
    assert has_permission("verify_cleanup", worker) is False
    assert has_permission("tune_weights", worker) is False
    assert has_permission("view_audit_logs", worker) is False

    with pytest.raises(PermissionError):
        enforce_permission("verify_cleanup", worker)

    # Citizen should only have submission and tracking rights
    citizen = {"role": "Citizen", "id": 8, "username": "citizen_priya"}
    assert has_permission("report_incident", citizen) is True
    assert has_permission("add_followup", citizen) is True
    assert has_permission("manage_tasks", citizen) is False
    assert has_permission("verify_cleanup", citizen) is False

    with pytest.raises(PermissionError):
        enforce_permission("manage_tasks", citizen)

    # Ward Officer has verification and escalation rights
    officer = {"role": "Ward Officer", "id": 2, "username": "officer_kora"}
    assert has_permission("verify_cleanup", officer) is True
    assert has_permission("escalate_case", officer) is True
    assert has_permission("tune_weights", officer) is False

    # Administrator has full system rights
    admin = {"role": "Administrator", "id": 1, "username": "admin_blr"}
    assert has_permission("tune_weights", admin) is True
    assert has_permission("view_audit_logs", admin) is True
    assert has_permission("verify_cleanup", admin) is True


def test_report_lifecycle_history_tracking(temp_repo):
    """Test multi-stage report lifecycle transitions with persistent audit history."""
    officer_id = temp_repo.create_user("officer_lc", "Officer Raman", "Ward Officer", ward="Koramangala")
    worker_id = temp_repo.create_user("worker_lc", "Worker Raju", "Cleanup Worker", ward="Koramangala")

    rep_id = temp_repo.create_report(
        report_uid="REP-LC-001",
        latitude=12.9352,
        longitude=77.6245,
        ward_name="Koramangala",
        waste_category="plastic",
        address="100ft Road 4th Block",
        is_simulated=1
    )
    assert rep_id > 0

    # Initial state
    rep = temp_repo.get_report_by_id(rep_id)
    assert rep["status"] == "Pending"

    # Transition 1: Under Review
    temp_repo.transition_report_status(rep_id, "Under Review", user_id=officer_id, user_name="Officer Raman", reason="Ward officer reviewing report")
    rep = temp_repo.get_report_by_id(rep_id)
    assert rep["status"] == "Under Review"

    # Transition 2: In Progress
    temp_repo.transition_report_status(rep_id, "In Progress", user_id=worker_id, user_name="Worker Raju", reason="Field team deployed")
    rep = temp_repo.get_report_by_id(rep_id)
    assert rep["status"] == "In Progress"

    # Transition 3: Awaiting Verification
    temp_repo.transition_report_status(rep_id, "Awaiting Verification", user_id=worker_id, user_name="Worker Raju", reason="Post-cleanup evidence uploaded")
    rep = temp_repo.get_report_by_id(rep_id)
    assert rep["status"] == "Awaiting Verification"

    # Transition 4: Verified Closed
    temp_repo.transition_report_status(rep_id, "Verified Closed", user_id=officer_id, user_name="Officer Raman", reason="Supervisor inspected and approved")
    rep = temp_repo.get_report_by_id(rep_id)
    assert rep["status"] == "Verified Closed"

    # Check history records (including initial 'Submitted')
    history = temp_repo.get_report_status_history(rep_id)
    assert len(history) >= 4
    statuses = [h["new_status"] for h in history]
    assert "Under Review" in statuses
    assert "In Progress" in statuses
    assert "Awaiting Verification" in statuses
    assert "Verified Closed" in statuses


def test_worker_field_operations_workflow(temp_repo):
    """Test worker assignment, acceptance, reporting blocked, and submission to verification queue."""
    sup_id = temp_repo.create_user("sup_wf", "Supervisor Suresh", "Sanitation Supervisor", ward="Indiranagar")
    worker_user_id = temp_repo.create_user("wrk_wf", "Worker Manju", "Cleanup Worker", ward="Indiranagar")

    rep_id = temp_repo.create_report(
        report_uid="REP-WRK-001",
        latitude=12.9719,
        longitude=77.6412,
        ward_name="Indiranagar",
        waste_category="construction",
        address="CMH Road Metro Pillar 42"
    )

    task_id = temp_repo.create_task(
        task_code="TASK-WRK-001",
        report_id=rep_id,
        assigned_team="Strike Gang Alpha",
        supervisor_id=sup_id,
        notes="Debris blocking pedestrian path"
    )

    # 1. Supervisor assigns worker
    temp_repo.assign_task_to_worker(task_id, worker_id=worker_user_id, supervisor_id=sup_id, notes="Assigned to Worker Manju")
    worker_tasks = temp_repo.get_tasks_for_worker(worker_user_id)
    assert len(worker_tasks) == 1
    assert worker_tasks[0]["task_code"] == "TASK-WRK-001"

    # 2. Worker accepts task
    temp_repo.worker_accept_task(task_id, worker_id=worker_user_id, worker_name="Worker Manju")
    t = next(x for x in temp_repo.get_all_tasks() if x["id"] == task_id)
    assert t["status"] == "In Progress"

    # 3. Worker reports task blocked (e.g. parked vehicles blocking access)
    temp_repo.worker_report_blocked(task_id, worker_id=worker_user_id, worker_name="Worker Manju", reason="Parked heavy vehicles blocking JCB entrance")
    t = next(x for x in temp_repo.get_all_tasks() if x["id"] == task_id)
    assert t["status"] == "Blocked"
    assert "Parked heavy vehicles" in (t.get("blocked_reason") or "")

    # 4. Worker resumes and submits for verification
    temp_repo.worker_submit_completion(
        task_id=task_id,
        worker_id=worker_user_id,
        worker_name="Worker Manju",
        before_img="",
        after_img="",
        notes="Area cleared after vehicle was towed away"
    )
    t = next(x for x in temp_repo.get_all_tasks() if x["id"] == task_id)
    assert t["status"] == "Awaiting Verification"


def test_citizen_followup_and_duplicate_matching(temp_repo):
    """Test citizen report follow-ups and spatial-temporal duplicate matching."""
    citizen_user_id = temp_repo.create_user("cit_priya", "Priya Sharma", "Citizen", ward="Koramangala")

    # Create original report
    rep1_id = temp_repo.create_report(
        report_uid="REP-CIT-001",
        latitude=12.9350,
        longitude=77.6240,
        ward_name="Koramangala",
        waste_category="organic_waste",
        address="8th Main 4th Block",
        citizen_id=citizen_user_id
    )

    # Citizen adds a follow-up clarification
    temp_repo.add_report_followup(
        report_id=rep1_id,
        user_id=citizen_user_id,
        user_name="Priya Sharma",
        notes="Stray cattle are now scattering the waste onto the road."
    )
    followups = temp_repo.get_report_followups(rep1_id)
    assert len(followups) == 1
    assert "Stray cattle" in followups[0]["notes"]

    # Citizen retrieves their personal reports
    cit_reports = temp_repo.get_reports_for_citizen(citizen_user_id)
    assert len(cit_reports) == 1
    assert cit_reports[0]["report_uid"] == "REP-CIT-001"

    # Test duplicate detection for nearby report in same ward within 50 meters
    dupes = temp_repo.find_duplicate_reports(
        lat=12.9351,
        lon=77.6241,
        max_meters=100.0
    )
    assert len(dupes) >= 1
    assert dupes[0]["report_uid"] == "REP-CIT-001"


def test_reporting_pdf_and_csv_generation(temp_repo, tmp_path):
    """Test generating real PDF dossiers and CSV exports."""
    rep_id = temp_repo.create_report(
        report_uid="REP-PDF-001",
        latitude=12.9352,
        longitude=77.6245,
        ward_name="Koramangala",
        waste_category="plastic",
        address="100ft Road",
        is_simulated=1
    )
    report = temp_repo.get_report_by_id(rep_id)

    # 1. Incident Dossier PDF
    res_path = generate_incident_pdf_report(report, "test_dossier.pdf")
    assert Path(res_path).exists()
    assert Path(res_path).stat().st_size > 500

    # 2. Ward Operations PDF
    all_reports = temp_repo.get_all_reports()
    res_ward = generate_ward_operations_pdf_report("Koramangala", all_reports, "test_ward.pdf")
    assert Path(res_ward).exists()
    assert Path(res_ward).stat().st_size > 500

    # 3. CSV generation
    csv_file = export_reports_to_csv(all_reports, "test_reports.csv")
    assert Path(csv_file).exists()
    content = Path(csv_file).read_text(encoding="utf-8")
    assert "REP-PDF-001" in content
    assert "Koramangala" in content


def test_civic_assistant_grounding(temp_repo):
    """Verify civic assistant grounds answers in database without hallucinating fake data."""
    rep_id = temp_repo.create_report(
        report_uid="REP-AST-999",
        latitude=12.9352,
        longitude=77.6245,
        ward_name="Koramangala",
        waste_category="medical_waste",
        address="St. Johns Hospital Road"
    )
    temp_repo.save_priority_score(
        report_id=rep_id,
        score=88.5,
        severity_comp=30.0,
        recurrence_comp=20.0,
        waste_type_comp=20.0,
        waiting_time_comp=18.5,
        rank=1
    )
    temp_repo.save_severity(
        report_id=rep_id,
        severity_level="High",
        severity_score=85.0,
        coverage_ratio=0.45,
        factors={"coverage": 45.0, "density": 0.8}
    )

    # Query for existing report
    ans = process_assistant_query("What is the status of REP-AST-999?", temp_repo)["response"]
    assert "REP-AST-999" in ans
    assert "Koramangala" in ans
    assert "Pending" in ans

    # Query for non-existent report
    ans_unknown = process_assistant_query("Tell me about report REP-FAKE-000", temp_repo)["response"]
    assert "REP-FAKE-000" in ans_unknown
    assert "no matching" in ans_unknown or "not found" in ans_unknown

    # General prioritization query
    ans_prio = process_assistant_query("How is priority calculated?", temp_repo)["response"]
    assert "Severity" in ans_prio
    assert "Recurrence" in ans_prio
    assert "Hazard" in ans_prio or "Waste Type" in ans_prio
