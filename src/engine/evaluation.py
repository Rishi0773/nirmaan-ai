"""
NIRMAAN AI - Evaluation & Comparative Simulation Engine
Compares NIRMAAN Priority-Based Dispatching against baseline First-Come-First-Served (FCFS)
ordering across high-severity wait times and critical hazard dwell periods (PPT Slide 2 & 9).
"""

from typing import Dict, List, Any
import pandas as pd
import numpy as np

from src.database.repository import Repository


def evaluate_fcfs_vs_priority(repo: Repository, crews_count: int = 2, cleanups_per_crew_day: int = 2) -> Dict[str, Any]:
    """
    Simulates operational cleanup dispatching under two queues:
    1. Baseline First-Come-First-Served (FIFO by creation timestamp)
    2. NIRMAAN Priority Queue (Sorted by calculated Priority Score)

    Calculates empirical dwell/waiting times (in days) to resolve high, medium, and low incidents.
    """
    reports = repo.get_all_reports()
    if not reports:
        return {"error": "No reports found for evaluation simulation."}

    # Prepare dataset
    items = []
    for r in reports:
        items.append({
            "id": r["id"],
            "uid": r["report_uid"],
            "ward": r["ward_name"],
            "category": r["waste_category"],
            "severity_level": r.get("severity_level") or "Medium",
            "severity_score": r.get("severity_score") or 50.0,
            "priority_score": r.get("priority_score") or 50.0,
            "created_at": r["created_at"],
            "status": r["status"]
        })

    df = pd.DataFrame(items)
    daily_capacity = max(1, crews_count * cleanups_per_crew_day)

    # 1. First-Come-First-Served (FCFS) Ordering: Sort purely by created_at
    fcfs_df = df.sort_values(by="created_at", ascending=True).copy().reset_index(drop=True)
    fcfs_df["fcfs_order"] = fcfs_df.index + 1
    # Waiting days under capacity simulation: index // daily_capacity + 0.5 day service
    fcfs_df["fcfs_wait_days"] = (fcfs_df.index // daily_capacity) + 0.5

    # 2. NIRMAAN Priority Ordering: Sort descending by priority_score
    prio_df = df.sort_values(by="priority_score", ascending=False).copy().reset_index(drop=True)
    prio_df["prio_order"] = prio_df.index + 1
    prio_df["prio_wait_days"] = (prio_df.index // daily_capacity) + 0.5

    # Comparative Metrics for High Severity Cases
    fcfs_high = fcfs_df[fcfs_df["severity_level"] == "High"]["fcfs_wait_days"].mean()
    prio_high = prio_df[prio_df["severity_level"] == "High"]["prio_wait_days"].mean()

    fcfs_med = fcfs_df[fcfs_df["severity_level"] == "Medium"]["fcfs_wait_days"].mean()
    prio_med = prio_df[prio_df["severity_level"] == "Medium"]["prio_wait_days"].mean()

    fcfs_low = fcfs_df[fcfs_df["severity_level"] == "Low"]["fcfs_wait_days"].mean()
    prio_low = prio_df[prio_df["severity_level"] == "Low"]["prio_wait_days"].mean()

    # Dwell time reduction for critical sites
    high_wait_reduction_pct = 0.0
    if fcfs_high and fcfs_high > 0:
        high_wait_reduction_pct = max(0.0, ((fcfs_high - prio_high) / fcfs_high) * 100.0)

    # Progression curve for cumulative severity cleared per day
    max_days = int(np.ceil(len(df) / daily_capacity))
    progression = []
    cum_fcfs_sev = 0.0
    cum_prio_sev = 0.0

    for d in range(1, max_days + 1):
        fcfs_day_slice = fcfs_df[(fcfs_df["fcfs_wait_days"] <= d)]
        prio_day_slice = prio_df[(prio_df["prio_wait_days"] <= d)]

        progression.append({
            "Day": d,
            "FCFS Cumulative Severity Resolved": round(float(fcfs_day_slice["severity_score"].sum()), 1),
            "NIRMAAN Cumulative Severity Resolved": round(float(prio_day_slice["severity_score"].sum()), 1)
        })

    prog_df = pd.DataFrame(progression)

    return {
        "total_tickets": len(df),
        "daily_capacity": daily_capacity,
        "fcfs_high_wait_days": round(float(fcfs_high or 0.0), 2),
        "prio_high_wait_days": round(float(prio_high or 0.0), 2),
        "high_wait_reduction_pct": round(float(high_wait_reduction_pct), 1),
        "fcfs_med_wait_days": round(float(fcfs_med or 0.0), 2),
        "prio_med_wait_days": round(float(prio_med or 0.0), 2),
        "fcfs_low_wait_days": round(float(fcfs_low or 0.0), 2),
        "prio_low_wait_days": round(float(prio_low or 0.0), 2),
        "progression_df": prog_df,
        "summary_table": pd.DataFrame([
            {"Severity": "High", "FCFS Avg Wait (Days)": round(fcfs_high or 0, 2), "NIRMAAN Avg Wait (Days)": round(prio_high or 0, 2), "Improvement": f"-{high_wait_reduction_pct:.1f}%"},
            {"Severity": "Medium", "FCFS Avg Wait (Days)": round(fcfs_med or 0, 2), "NIRMAAN Avg Wait (Days)": round(prio_med or 0, 2), "Improvement": "Balanced"},
            {"Severity": "Low", "FCFS Avg Wait (Days)": round(fcfs_low or 0, 2), "NIRMAAN Avg Wait (Days)": round(prio_low or 0, 2), "Improvement": "Deferred"},
        ])
    }
