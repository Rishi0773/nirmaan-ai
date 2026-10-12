"""
NIRMAAN AI - Transparent Prioritization Engine
Implements the explainable mathematical scoring formula balancing
Severity, Recurrence, Waste Type, and Waiting Time (PPT Slide 7).
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import numpy as np

from src.config import DEFAULT_PRIORITY_WEIGHTS, WASTE_TYPE_WEIGHTS
from src.database.repository import Repository


def compute_priority_score(
    severity_score: float,
    recurrence_score: float,
    waste_category: str,
    created_at_str: Optional[str] = None,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Computes explainable cleanup priority score.
    Formula: Score = w_s * S + w_r * R + w_w * W + w_t * T
    All components normalized to [0, 100].
    """
    w = weights or DEFAULT_PRIORITY_WEIGHTS

    # 1. Severity Component (S)
    S = float(np.clip(severity_score, 0.0, 100.0))

    # 2. Recurrence Component (R)
    R = float(np.clip(recurrence_score, 0.0, 100.0))

    # 3. Waste Type Hazard Component (W)
    W = float(WASTE_TYPE_WEIGHTS.get(waste_category.lower(), 60.0))

    # 4. Pending Waiting Time Component (T)
    # 8 days pending = 100 max urgency score; scale linearly
    elapsed_days = 0.0
    if created_at_str:
        try:
            dt = datetime.strptime(created_at_str[:19], "%Y-%m-%d %H:%M:%S")
            elapsed_days = max(0.0, (datetime.now() - dt).total_seconds() / 86400.0)
        except Exception:
            elapsed_days = 1.0

    T = float(np.clip(elapsed_days * 12.5, 5.0, 100.0))

    # Weighted Sum
    total_score = (
        w["severity"] * S +
        w["recurrence"] * R +
        w["waste_type"] * W +
        w["waiting_time"] * T
    )
    final_score = round(float(np.clip(total_score, 0.0, 100.0)), 1)

    # Individual contributions
    contrib_sev = round(w["severity"] * S, 1)
    contrib_rec = round(w["recurrence"] * R, 1)
    contrib_waste = round(w["waste_type"] * W, 1)
    contrib_time = round(w["waiting_time"] * T, 1)

    # Recommended Action
    if final_score >= 80.0:
        recommended_action = "CRITICAL: Immediate dispatch required within 6 hours."
    elif final_score >= 60.0:
        recommended_action = "HIGH: Schedule sanitation strike team within 24 hours."
    elif final_score >= 40.0:
        recommended_action = "MODERATE: Address during standard ward beat (48 hours)."
    else:
        recommended_action = "LOW: Routine scheduled collection."

    return {
        "final_score": final_score,
        "elapsed_days": round(elapsed_days, 1),
        "components": {
            "severity_value": S,
            "recurrence_value": R,
            "waste_type_value": W,
            "waiting_time_value": round(T, 1)
        },
        "contributions": {
            "severity_contrib": contrib_sev,
            "recurrence_contrib": contrib_rec,
            "waste_type_contrib": contrib_waste,
            "waiting_time_contrib": contrib_time
        },
        "weights_used": w,
        "recommended_action": recommended_action
    }


def calculate_and_save_all_priorities(repo: Repository, custom_weights: Optional[Dict[str, float]] = None):
    """
    Recalculates priority scores across all non-cleared reports,
    ranks them, and updates the priority_scores table.
    """
    reports = repo.get_all_reports()
    if not reports:
        return

    # Map reports to their hotspot recurrence score if clustered
    hotspots = repo.get_all_hotspots()
    hotspot_map = {}
    for hs in hotspots:
        hs_reports = repo.get_hotspot_reports(hs["id"])
        for hr in hs_reports:
            hotspot_map[hr["id"]] = hs["recurrence_score"]

    computed_list = []
    for r in reports:
        rep_id = r["id"]
        sev_score = r.get("severity_score") or 50.0
        rec_score = hotspot_map.get(rep_id, 20.0)
        waste_cat = r.get("waste_category") or "mixed_trash"
        created_at = r.get("created_at")

        calc = compute_priority_score(
            severity_score=sev_score,
            recurrence_score=rec_score,
            waste_category=waste_cat,
            created_at_str=created_at,
            weights=custom_weights
        )

        computed_list.append({
            "report_id": rep_id,
            "calc": calc,
            "status": r["status"]
        })

    # Sort descending by priority score
    computed_list.sort(key=lambda x: x["calc"]["final_score"], reverse=True)

    for rank_idx, item in enumerate(computed_list, start=1):
        c = item["calc"]
        repo.save_priority_score(
            report_id=item["report_id"],
            score=c["final_score"],
            severity_comp=c["contributions"]["severity_contrib"],
            recurrence_comp=c["contributions"]["recurrence_contrib"],
            waste_type_comp=c["contributions"]["waste_type_contrib"],
            waiting_time_comp=c["contributions"]["waiting_time_contrib"],
            rank=rank_idx
        )
