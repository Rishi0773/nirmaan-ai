"""
NIRMAAN AI - Civic Assistant Service
Provides grounded, accurate decision-support, database-backed report tracking,
formula explanations, and role-aware navigation connected directly to SQLite storage.
"""

import re
from typing import Dict, Any, Optional
from src.database.repository import Repository
from src.config import DEFAULT_PRIORITY_WEIGHTS, SEVERITY_THRESHOLDS, CIVIC_DISCLAIMER
from src.auth.rbac import get_current_user


def process_assistant_query(query: str, repo: Repository) -> Dict[str, Any]:
    """
    Processes user queries strictly grounded in real database records,
    application services, active priority weights, and user role scope.
    """
    q = query.strip().lower()
    user = get_current_user()
    role = user.get("role", "Citizen")

    # 1. Direct UID tracking (e.g. REP-BLR-001 or REP-...)
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
            cat = report.get("waste_category", "mixed_trash").replace('_', ' ').title()

            # Check for verification records
            tasks = repo.get_all_tasks()
            linked_task = next((t for t in tasks if t["report_id"] == report["id"]), None)
            task_info = ""
            if linked_task:
                t_st = linked_task["status"]
                t_team = linked_task["assigned_team"]
                task_info = f"\n- **Dispatched Strike Team:** {t_team} (`{t_st}`)"
                ver = repo.get_verification_by_task(linked_task["id"])
                if ver:
                    task_info += f"\n- **Field Verification:** {ver['supervisor_decision']} ({ver['waste_reduction_pct']:.1f}% reduction recorded)"

            sim_note = " *(Simulated demonstration record)*" if report.get("is_simulated") else ""

            return {
                "response": (
                    f"**Verified Record Found: {target_uid}**{sim_note}\n\n"
                    f"- **Lifecycle Status:** `{st}`\n"
                    f"- **Ward & Address:** {ward} — {addr[:45]}\n"
                    f"- **Waste Category:** {cat}\n"
                    f"- **Computer Vision Severity:** `{sev}` (Score: {report.get('severity_score', 0):.1f}/100)\n"
                    f"- **Priority Score:** `{prio:.1f}/100` "
                    f"($S$={report.get('severity_component', 0):.1f}, $R$={report.get('recurrence_component', 0):.1f}, $W$={report.get('waste_type_component', 0):.1f}, $T$={report.get('waiting_time_component', 0):.1f}){task_info}\n\n"
                    f"Click below to inspect the complete photographic evidence dossier."
                ),
                "action": "view_dossier",
                "report_uid": target_uid,
                "action_label": "Go to Incident Dossier"
            }
        else:
            return {
                "response": (
                    f"I queried the municipal SQLite database for **{target_uid}**, but no matching complaint was found. "
                    "Please verify the ticket ID (e.g. `REP-BLR-001`) or search by ward name."
                ),
                "action": None
            }

    # 2. Task lookup (e.g. TASK-001 or TASK-...)
    task_match = re.search(r"task-[a-z0-9\-]+", q)
    if task_match:
        target_code = task_match.group(0).upper()
        tasks = repo.get_all_tasks()
        target_t = next((t for t in tasks if t["task_code"] == target_code), None)
        if target_t:
            return {
                "response": (
                    f"**Work Order Found: {target_code}**\n"
                    f"- **Linked Report:** `{target_t['report_uid']}` ({target_t['ward_name']})\n"
                    f"- **Assigned Team:** {target_t['assigned_team']}\n"
                    f"- **Status:** `{target_t['status']}`\n"
                    f"- **Scheduled Date:** {target_t['created_at']}\n"
                    f"- **Notes:** {target_t.get('notes') or 'Standard clearance order'}"
                ),
                "action": "navigate_queue",
                "action_label": "View Task Operations"
            }
        else:
            return {
                "response": f"Work order **{target_code}** was not found in the operations database.",
                "action": None
            }

    # 3. How to report inquiry
    if any(k in q for k in ["how do i report", "report a garbage", "file a complaint", "how to report", "submit waste"]):
        return {
            "response": (
                "**How to file a garbage report in NIRMAAN AI:**\n"
                "1. Click **'Report Garbage'** in the top navigation.\n"
                "2. Upload a daytime photograph of the waste accumulation.\n"
                "3. Select your Bengaluru ward and confirm GPS coordinates.\n"
                "4. Select the primary waste category (Plastic, Organic, Mixed, or Hazardous).\n"
                "5. Submit! YOLOv8 and OpenCV will immediately analyze bounding boxes and ground coverage to rank the complaint."
            ),
            "action": "navigate_report",
            "action_label": "Open Incident Reporting Form"
        }

    # 4. Track status intent without UID
    if any(k in q for k in ["track", "status of", "check complaint", "my complaint"]):
        recent = repo.get_all_reports()[:4]
        recent_uids = ", ".join([f"`{r['report_uid']}`" for r in recent]) if recent else "None"
        return {
            "response": (
                "To track a specific complaint, please provide your **Report UID** (e.g. `REP-BLR-001`).\n\n"
                f"Recent active tickets in the database: {recent_uids}."
            ),
            "action": "navigate_dossier",
            "action_label": "Go to Incident Dossier"
        }

    # 5. Hotspot map intent
    if any(k in q for k in ["map", "hotspot", "cluster", "where are", "blackspot"]):
        hotspots = repo.get_all_hotspots()
        active_count = len(hotspots)
        return {
            "response": (
                f"The **Live Hotspot Map** currently tracks **{active_count} active geospatial clusters** "
                "across Bengaluru wards. Spatial clusters are grouped using Scikit-learn DBSCAN with a 200m buffer "
                "to prioritize chronic dumping blackspots."
            ),
            "action": "navigate_map",
            "action_label": "Open Live Hotspot Map"
        }

    # 6. Priority calculation & formula
    if any(k in q for k in ["priority", "formula", "score", "calculate", "how is priority", "weight"]):
        w = DEFAULT_PRIORITY_WEIGHTS
        return {
            "response": (
                "**NIRMAAN AI Explainable Prioritization Formula**\n\n"
                "Priority Score ($P$) is calculated using weighted civic factors:\n\n"
                f"$$\nP = {w['severity']:.2f}S + {w['recurrence']:.2f}R + {w['waste_type']:.2f}W + {w['waiting_time']:.2f}T\n$$\n\n"
                f"- **Severity ($S$, {int(w['severity']*100)}%):** YOLOv8 object count and OpenCV ground surface coverage ratio.\n"
                f"- **Recurrence ($R$, {int(w['recurrence']*100)}%):** Frequency of repeat incidents within a 200m DBSCAN cluster.\n"
                f"- **Hazard ($W$, {int(w['waste_type']*100)}%):** Urgency penalty for biomedical, decaying organic, or hazardous waste.\n"
                f"- **Waiting Time ($T$, {int(w['waiting_time']*100)}%):** Starvation prevention escalator preventing older complaints from languishing."
            ),
            "action": "navigate_queue",
            "action_label": "Inspect Priority Queue"
        }

    # 7. Severity tiers explanation
    if any(k in q for k in ["severity", "level", "threshold", "grade"]):
        t = SEVERITY_THRESHOLDS
        return {
            "response": (
                "**Severity Classification Standards:**\n"
                f"- **LOW:** $\\le {t['low_max_objects']}$ objects and $\\le {t['low_max_coverage']}\\%$ ground coverage.\n"
                f"- **MEDIUM:** $\\le {t['med_max_objects']}$ objects or up to ${t['med_max_coverage']}\\%$ coverage.\n"
                "- **HIGH:** $>40\\%$ coverage, $>6$ items, or ANY biohazard/medical waste accumulation."
            ),
            "action": None
        }

    # 8. Dashboard statistics summary
    if any(k in q for k in ["statistic", "summary", "how many", "total", "metrics", "kpi"]):
        m = repo.get_dashboard_metrics()
        return {
            "response": (
                "**Live Municipal Decision-Support Metrics:**\n"
                f"- Total Logged Reports: **{m['total_reports']}**\n"
                f"- High-Severity Pending Dispatches: **{m['high_severity_pending']}**\n"
                f"- Active DBSCAN Hotspots: **{m['active_hotspots']}**\n"
                f"- Work Orders Under Field Cleanup: **{m['under_cleanup']}**\n"
                f"- Verified Closed Sites: **{m['cleared_reports']}**\n"
                f"- Average Priority Score: **{m['avg_priority_score']}/100**"
            ),
            "action": "navigate_dashboard",
            "action_label": "Open Municipal Analytics"
        }

    # 9. Ward specific inquiries
    wards = ["koramangala", "indiranagar", "malleshwaram", "whitefield", "jayanagar", "shivajinagar", "hsr layout"]
    for w in wards:
        if w in q:
            all_reps = [r for r in repo.get_all_reports() if r["ward_name"].lower() == w]
            pending = [r for r in all_reps if r["status"] != "Cleared"]
            hotspots_w = [h for h in repo.get_all_hotspots() if h.get("ward_name", "").lower() == w]
            return {
                "response": (
                    f"**Operational Status for {w.title()} Ward:**\n"
                    f"- Total Incidents Recorded: **{len(all_reps)}**\n"
                    f"- Unresolved / In-Progress: **{len(pending)}**\n"
                    f"- Active DBSCAN Clusters: **{len(hotspots_w)}**\n"
                    f"Cleanups are prioritized by computer vision severity and repeat dumping frequency."
                ),
                "action": "navigate_dashboard",
                "action_label": f"View {w.title()} Analytics"
            }

    # 10. Role specific inquiries
    if "my role" in q or "who am i" in q:
        return {
            "response": (
                f"You are currently logged in as **{user['full_name']}** with role **{role}** "
                f"assigned to ward **{user.get('ward_assigned', 'Central')}**.\n\n"
                f"Switch identity anytime via the 'Civic Portal' navigation link."
            ),
            "action": None
        }

    # 11. System limitations and disclaimers
    if any(k in q for k in ["limitation", "accuracy", "disclaimer", "bbmp", "official"]):
        return {
            "response": (
                "**System Transparency & Boundaries:**\n"
                f"• {CIVIC_DISCLAIMER}\n"
                "• Computer vision ground coverage is calculated from 2D images and serves as a proxy for real-world volume.\n"
                "• Pre-loaded demonstration data represents simulated municipal reports for algorithmic evaluation."
            ),
            "action": None
        }

    # Disambiguation / Clarification fallback
    return {
        "response": (
            "I am your NIRMAAN Civic Decision-Support Assistant. Could you please clarify your request?\n\n"
            "You can ask me to:\n"
            "• **Track a report:** Type your ticket ID (e.g. `Track REP-BLR-001`)\n"
            "• **Check ward status:** Ask about `Koramangala`, `Indiranagar`, or `Malleshwaram`\n"
            "• **Explain triage:** Ask `How is priority calculated?` or `What does high severity mean?`\n"
            "• **System metrics:** Ask `Show summary statistics`"
        ),
        "action": None
    }
