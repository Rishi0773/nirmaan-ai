"""
NIRMAAN AI - Recurrence Analytics & Historical Frequency
Analyzes temporal intervals between repeat incidents at known spatial hotspots.
Adheres strictly to academic honesty: provides baseline empirical frequency indicators
and documents that longitudinal validation datasets are required for ML forecasting.
"""

from datetime import datetime
from typing import Dict, List, Any
import numpy as np


def analyze_hotspot_recurrence(hotspot_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes empirical repeat intervals and recurrence risk for a cluster.
    Returns transparent recurrence index [0.0, 100.0] and academic disclaimers.
    """
    if not hotspot_reports or len(hotspot_reports) < 2:
        return {
            "recurrence_index": 15.0,
            "repeat_count": len(hotspot_reports),
            "avg_interval_days": None,
            "recurrence_risk_level": "Low (Isolated)",
            "rationale": "Single isolated report. Insufficient historical observations to establish recurrence pattern.",
            "academic_notice": "Baseline calculation only; predictive machine learning models require longitudinal labeled time-series."
        }

    # Sort reports chronologically
    dates = []
    for r in hotspot_reports:
        created_str = r.get("created_at")
        if created_str:
            try:
                dt = datetime.strptime(created_str[:19], "%Y-%m-%d %H:%M:%S")
                dates.append(dt)
            except Exception:
                pass

    dates.sort()
    count = len(dates)

    if len(dates) >= 2:
        intervals = [(dates[i] - dates[i - 1]).total_seconds() / 86400.0 for i in range(1, len(dates))]
        avg_interval = float(np.mean(intervals))
    else:
        avg_interval = 7.0

    # Short intervals (< 3 days) indicate chronic dumping; longer (> 14 days) indicate sporadic litter
    if avg_interval <= 3.0:
        risk_level = "High (Chronic Daily Re-dumping)"
        base_index = 90.0
    elif avg_interval <= 7.0:
        risk_level = "Elevated (Weekly Recurrence)"
        base_index = 72.0
    else:
        risk_level = "Moderate (Sporadic Repeat)"
        base_index = 45.0

    # Scale with volume
    recurrence_index = float(np.clip(base_index + (count * 2.5), 0.0, 100.0))

    return {
        "recurrence_index": round(recurrence_index, 1),
        "repeat_count": count,
        "avg_interval_days": round(avg_interval, 1),
        "recurrence_risk_level": risk_level,
        "rationale": f"Cluster exhibits repeat dumping approximately every {avg_interval:.1f} days across {count} logged incidents.",
        "academic_notice": "Observed recurrence frequency computed from empirical report timestamps. Predictive models require ongoing municipal ground-truth calibration."
    }
