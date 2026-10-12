"""
NIRMAAN AI - Unit Tests: FCFS vs. Priority Queue Simulation Engine
"""

import pytest
from datetime import datetime, timedelta
from src.database.connection import init_db
from src.database.repository import Repository
from src.engine.evaluation import evaluate_fcfs_vs_priority


def test_evaluation_simulation(tmp_path):
    test_db = tmp_path / "test_eval.db"
    init_db(test_db)
    repo = Repository(test_db)

    now = datetime.now()
    # Add an old low-severity report (created 5 days ago)
    r1 = repo.create_report(
        "REP-OLD-LOW", 12.9352, 77.6245, "Koramangala", "paper",
        created_at=(now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
    )
    repo.save_severity(r1, "Low", 20.0, 8.0, {})
    repo.save_priority_score(r1, score=25.0, severity_comp=7.0, recurrence_comp=5.0, waste_type_comp=7.0, waiting_time_comp=6.0)

    # Add a fresh high-severity hazard report (created today)
    r2 = repo.create_report(
        "REP-NEW-HIGH", 12.9719, 77.6412, "Indiranagar", "hazardous",
        created_at=now.strftime("%Y-%m-%d %H:%M:%S")
    )
    repo.save_severity(r2, "High", 95.0, 50.0, {})
    repo.save_priority_score(r2, score=92.0, severity_comp=33.0, recurrence_comp=20.0, waste_type_comp=19.0, waiting_time_comp=20.0)

    res = evaluate_fcfs_vs_priority(repo, crews_count=1, cleanups_per_crew_day=1)

    assert "total_tickets" in res
    assert res["total_tickets"] == 2
    # In FCFS, the high severity report had to wait behind the low severity report
    # In NIRMAAN, high severity was prioritized first (lower or equal wait time)
    assert res["prio_high_wait_days"] <= res["fcfs_high_wait_days"]
