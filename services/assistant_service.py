"""
NIRMAAN AI - Civic Assistant Service
Provides rule-based civic decision-support, report tracking, formula explanation,
and navigation dispatching connected directly to the SQLite repository.
"""

import re
from typing import Dict, Any, Optional
from src.database.repository import Repository
from src.config import DEFAULT_PRIORITY_WEIGHTS, SEVERITY_THRESHOLDS


def process_assistant_query(query: str, repo: Repository) -> Dict[str, Any]:
    """
    Processes user query and returns a structured response with guidance
    and optional UI navigation actions.
    """
    q = query.strip().lower()

    # 1. Report hotpot / how to report
    if "how do i report" in q or "report a garbage" in q or "file a complaint" in q or "new report" in q:
        return {
            "response": (
                "To report a garbage hotspot:\n"
                "1. Click **'Report Garbage'** in the navigation.\n"
                "2. Upload a photograph of the waste accumulation.\n"
                "3. Select your Bengaluru ward and pinpoint coordinates.\n"
                "4. Select the waste category (e.g., Plastic, Organic, Hazardous).\n"
                "5. Submit! The YOLOv8 computer vision engine will immediately grade the severity and queue it for dispatch."
            ),
            "action": "navigate_report",
            "action_label": "Open Incident Reporting Form"
        }

    # 2. Track report intent
    # Check for direct UID pattern like REP-BLR-001 or REP-...
    uid_match = re.search(r"rep-[a-z0-9\-]+", q)
    if uid_match:
        target_uid = uid_match.group(0).upper()
        report = repo.get_report_by_uid(target_uid)
        if report:
            prio = report.get("priority_score", 0.0)
            sev = report.get("severity_level", "Medium")
            st = report.get("status", "Pending")
            ward = report.get("ward_name", "Bengaluru")
            addr = report.get("address", "")
            return {
                "response": (
                    f"**Ticket Found: {target_uid}**\n"
                    f"- **Status:** `{st}`\n"
                    f"- **Ward:** {ward} ({addr[:40]})\n"
                    f"- **CV Severity:** `{sev}`\n"
                    f"- **Priority Score:** `{prio:.1f}/100`\n"
                    f"You can view full evidence photos and detection bounding boxes in the Incident Dossier."
                ),
                "action": "view_dossier",
                "report_uid": target_uid,
                "action_label": f"View Dossier for {target_uid}"
            }
        else:
            return {
                "response": f"I searched the civic database but could not find report **{target_uid}**. Please check the ID or search by ward name.",
                "action": None
            }

    if "track" in q or "status of" in q:
        recent = repo.get_all_reports()[:3]
        recent_uids = ", ".join([f"`{r['report_uid']}`" for r in recent]) if recent else "None"
        return {
            "response": (
                "To track your report, please type your exact Report UID (e.g. `REP-BLR-001`).\n\n"
                f"Recent active tickets in the system: {recent_uids}."
            ),
            "action": "navigate_dossier",
            "action_label": "Go to Incident Dossier"
        }

    # 3. Show hotspot map
    if "map" in q or "hotspot map" in q or "where" in q:
        hotspots = repo.get_all_hotspots()
        active_count = len(hotspots)
        return {
            "response": (
                f"The **Live Hotspot Map** currently tracks **{active_count} active geospatial clusters** "
                "across Bengaluru. Areas are clustered using DBSCAN within a 200m radius to prioritize repeat blackspots."
            ),
            "action": "navigate_map",
            "action_label": "Open Live Hotspot Map"
        }

    # 4. Severity levels
    if "severity" in q or "level" in q or "grade" in q:
        t = SEVERITY_THRESHOLDS
        return {
            "response": (
                "NIRMAAN AI classifies incident severity into 3 standardized tiers:\n"
                f"- **LOW**: $\\le {t['low_max_objects']}$ detected waste items and $\\le {t['low_max_coverage']}\\%$ OpenCV ground coverage.\n"
                f"- **MEDIUM**: $\\le {t['med_max_objects']}$ detected items or ${t['low_max_coverage']}\\%$ to ${t['med_max_coverage']}\\%$ coverage.\n"
                "- **HIGH**: Overflowing heaps ($>40\\%$ coverage, $>6$ items) OR any hazardous/medical waste."
            ),
            "action": None
        }

    # 5. Priority calculation
    if "priority" in q or "calculate" in q or "formula" in q or "score" in q:
        w = DEFAULT_PRIORITY_WEIGHTS
        return {
            "response": (
                "Cleanup priority is calculated mathematically via an explainable 4-component index:\n\n"
                f"$$\\text{{Score}} = {w['severity']}\\cdot S + {w['recurrence']}\\cdot R + {w['waste_type']}\\cdot W + {w['waiting_time']}\\cdot T$$\n\n"
                "- **$S$ (Severity, 35%)**: Computer vision volume & object count.\n"
                "- **$R$ (Recurrence, 25%)**: Repeat complaint frequency within 200m DBSCAN cluster.\n"
                "- **$W$ (Waste Hazard, 20%)**: High urgency for biomedical/decaying organic matter.\n"
                "- **$T$ (Wait Time, 20%)**: Normalized escalation for pending complaints."
            ),
            "action": "navigate_queue",
            "action_label": "Inspect Priority Queue"
        }

    # 6. Ward query
    wards = ["koramangala", "indiranagar", "malleshwaram", "whitefield", "jayanagar"]
    for w in wards:
        if w in q:
            all_reps = [r for r in repo.get_all_reports() if r["ward_name"].lower() == w]
            pending = [r for r in all_reps if r["status"] != "Cleared"]
            return {
                "response": (
                    f"**Ward Summary: {w.title()}**\n"
                    f"- Total Complaints: **{len(all_reps)}**\n"
                    f"- Unresolved / Pending: **{len(pending)}**\n"
                    f"- Monitored Hotspot: Active spatial clusters monitored by BBMP field crews."
                ),
                "action": "navigate_dashboard",
                "action_label": "Open Civic Dashboard"
            }

    # Default fallback response
    return {
        "response": (
            "I can assist you with reporting garbage blackspots, checking complaint status, "
            "understanding severity grades, or reviewing Bengaluru hotspot clusters.\n\n"
            "Try asking: *'Track REP-BLR-001'*, *'How is priority calculated?'*, or *'Show hotspot map'*."
        ),
        "action": None
    }
