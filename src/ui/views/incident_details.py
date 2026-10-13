"""
NIRMAAN AI - Incident Details & Timeline History View
Deep-dive into a specific garbage report: computer vision telemetry,
severity grading factors, priority score breakdown, lifecycle timeline, and follow-up observations.
"""

from pathlib import Path
import streamlit as st
from src.database.repository import Repository
from src.ui.components import render_header, severity_badge_html, status_badge_html
from src.auth.rbac import has_permission, get_current_user


def render(repo: Repository):
    render_header(
        title="Incident Dossier & Evidence History",
        subtitle="Detailed inspection of computer vision telemetry, scoring components, and operational records.",
        active_tab="Incident Details"
    )

    reports = repo.get_all_reports()
    if not reports:
        st.info("No incident reports found in database.")
        return

    # Selector
    report_options = [f"{r['report_uid']} - {r['ward_name']} ({r['status']})" for r in reports]
    default_idx = 0
    if "selected_report_uid" in st.session_state:
        for idx, r in enumerate(reports):
            if r["report_uid"] == st.session_state["selected_report_uid"]:
                default_idx = idx
                break
    selected_option = st.selectbox("Select Incident Ticket to Inspect", options=report_options, index=default_idx)
    selected_uid = selected_option.split(" - ")[0]

    report = repo.get_report_by_uid(selected_uid)
    if not report:
        st.error(f"Report {selected_uid} not found.")
        return

    rep_id = report["id"]
    images = repo.get_report_images(rep_id)

    # 1. Ticket Header Summary Card
    sim_badge = '<span class="badge badge-med">SIMULATED DEMO RECORD</span>' if report['is_simulated'] else '<span class="badge badge-low">FIELD CIVIC OBSERVATION</span>'

    st.markdown(
        f"""
        <div class="neu-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
                <div>
                    <h2 style="margin: 0; color: #0F172A; font-size: 1.35rem;">
                        Ticket: {report['report_uid']}
                    </h2>
                    <span style="font-size: 0.85rem; color: #64748B;">
                        Reported: {report['created_at']} | Ward: <strong>{report['ward_name']}</strong>
                    </span>
                </div>
                <div>
                    {status_badge_html(report['status'])}
                    {sim_badge}
                </div>
            </div>
            <div style="font-size: 0.9rem; color: #334155; margin-top: 0.5rem;">
                <strong>Location:</strong> {report['address'] or 'Street coordinates recorded'}
                ({report['latitude']:.4f}, {report['longitude']:.4f})
            </div>
            <div style="font-size: 0.88rem; color: #475569; margin-top: 0.25rem;">
                <strong>Citizen Description:</strong> {report['description'] or 'No description provided.'}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Imagery: Original vs Annotated
    st.markdown("### Computer Vision Inspection")
    img_col1, img_col2 = st.columns(2)

    incident_img = next((img for img in images if img["image_type"] == "incident"), None)

    with img_col1:
        st.markdown("<strong>Original Submitted Photograph</strong>", unsafe_allow_html=True)
        if incident_img and Path(incident_img["file_path"]).exists():
            st.image(incident_img["file_path"], use_container_width=True)
        else:
            st.info("Original image file logged.")

    with img_col2:
        st.markdown("<strong>YOLOv8 Bounding Boxes & Saliency Mask</strong>", unsafe_allow_html=True)
        if incident_img and incident_img.get("annotated_path") and Path(incident_img["annotated_path"]).exists():
            st.image(incident_img["annotated_path"], use_container_width=True)
        elif incident_img and Path(incident_img["file_path"]).exists():
            st.image(incident_img["file_path"], caption="Bounding box overlay", use_container_width=True)
        else:
            st.info("Annotated detections logged.")

    # 3. Telemetry & Scoring Breakdown
    t_col1, t_col2 = st.columns(2)

    with t_col1:
        st.markdown("### Severity Assessment Details")
        st.markdown(
            f"""
            <div class="neu-card">
                <div style="margin-bottom: 0.5rem;">
                    Level: {severity_badge_html(report.get('severity_level'))}
                </div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">
                    Severity Score: {report.get('severity_score', 0):.1f}/100
                </div>
                <div style="font-size: 0.85rem; color: #475569; margin-top: 0.5rem;">
                    <div>• Ground Coverage: <strong>{report.get('coverage_ratio', 0):.1f}%</strong></div>
                    <div>• Detected Objects: <strong>{report.get('total_objects', 0)} items</strong></div>
                    <div>• Waste Category: <strong>{report['waste_category'].replace('_', ' ').title()}</strong></div>
                    <div>• Model Version: <strong>{report.get('model_version', 'NIRMAAN-YOLOv8')}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with t_col2:
        st.markdown("### Prioritization Score Breakdown")
        prio_score = report.get('priority_score', 0)
        st.markdown(
            f"""
            <div class="neu-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; color: #64748B; font-weight: 600;">NIRMAAN COMPOSITE SCORE</span>
                    <span class="prio-pill">{prio_score:.1f} / 100</span>
                </div>
                <div style="margin-top: 0.75rem; font-size: 0.82rem; color: #334155; line-height: 1.6;">
                    <div>• Severity Contribution: <strong>+{report.get('severity_component', 0):.1f} pts</strong> (Weight: 35%)</div>
                    <div>• Recurrence Contribution: <strong>+{report.get('recurrence_component', 0):.1f} pts</strong> (Weight: 25%)</div>
                    <div>• Waste Hazard Contribution: <strong>+{report.get('waste_type_component', 0):.1f} pts</strong> (Weight: 20%)</div>
                    <div>• Waiting Time Urgency: <strong>+{report.get('waiting_time_component', 0):.1f} pts</strong> (Weight: 20%)</div>
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.75rem; color: #64748B; font-style: italic;">
                    Formula: Score = 0.35·S + 0.25·R + 0.20·W + 0.20·T
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 4. Status Transition Lifecycle Timeline
    st.markdown("### Status Lifecycle & Verification History")
    history = repo.get_report_status_history(rep_id)

    if history:
        for idx, h in enumerate(history, 1):
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #10B981; border-radius: 8px; padding: 0.6rem 0.9rem; margin-bottom: 0.45rem; font-size: 0.85rem; color: #1E293B;">
                    <strong>Step {idx}:</strong> <code>{h.get('old_status') or 'Init'}</code> &rarr; <strong>{h['new_status']}</strong>
                    <span style="color: #64748B; font-size: 0.8rem; margin-left: 0.5rem;">({h['created_at']} by {h.get('changed_by_name') or 'System'})</span>
                    <div style="font-size: 0.8rem; color: #475569; margin-top: 0.2rem;">
                        Notes: {h.get('reason') or 'Status transition recorded'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No transition records logged yet.")

    # 5. Follow-ups & Citizen Notes
    st.markdown("### Follow-up Observations")
    followups = repo.get_report_followups(rep_id)
    if followups:
        for f in followups:
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 0.5rem 0.75rem; margin-bottom: 0.35rem; font-size: 0.82rem;">
                    <strong>{f.get('user_name', 'Citizen')}</strong> ({f['created_at']}): {f['notes']}
                </div>
                """, unsafe_allow_html=True
            )

    user = get_current_user()
    with st.expander("Add Follow-up Observation to this Ticket"):
        new_f_note = st.text_input("Enter observation note", key="new_followup_dossier")
        if st.button("Append Follow-up Note", type="primary") and new_f_note.strip():
            repo.add_report_followup(rep_id, user["id"], user["full_name"], new_f_note.strip())
            st.success("Follow-up observation appended!")
            st.rerun()

    # 6. Operational Actions (Role-gated)
    if has_permission("manage_tasks"):
        st.markdown("### Operational Actions (Authorized)")
        act_col1, act_col2 = st.columns(2)

        with act_col1:
            if report["status"] in ["Pending", "Submitted"]:
                if st.button("Dispatch Sanitation Strike Team", type="primary", use_container_width=True):
                    task_code = f"TASK-{report['report_uid'][-4:]}"
                    repo.create_task(
                        task_code=task_code,
                        report_id=report["id"],
                        assigned_team="Ward Rapid Strike Team",
                        supervisor_id=user["id"],
                        priority_level="High" if report.get("severity_level") == "High" else "Normal",
                        notes="Dispatched via Incident Dossier."
                    )
                    repo.log_audit("TASK_CREATE", "Task", task_code, user["full_name"], user["id"], "Pending", "Under Cleanup")
                    st.success(f"Task {task_code} dispatched! Ticket status updated to Under Cleanup.")
                    st.rerun()

        with act_col2:
            if report["status"] in ["Cleared", "Verified Closed"] and has_permission("reopen_case"):
                if st.button("Reopen Incident (Incomplete Clearance)", use_container_width=True):
                    repo.transition_report_status(report["id"], "Reopened", user["id"], user["full_name"], "Reopened by officer for re-cleaning.")
                    st.warning("Incident reopened for field inspection.")
                    st.rerun()
