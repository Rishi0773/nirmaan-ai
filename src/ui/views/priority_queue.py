"""
NIRMAAN AI - Ranked Cleanup Queue View
Displays dynamically prioritized cleanup tickets with transparent factor contributions,
explainable score breakdowns, and supervisor manual override capabilities (PPT Slide 3 & 7).
"""

import streamlit as st
from src.database.repository import Repository
from src.ui.components import render_header, severity_badge_html, status_badge_html
from src.auth.rbac import has_permission, get_current_user


def render(repo: Repository):
    render_header(
        title="Ranked Cleanup Priority Queue",
        subtitle="Dynamic municipal triage ranking based on computer vision severity, recurrence, hazard, and waiting time.",
        active_tab="Priority Queue"
    )

    reports = repo.get_all_reports()
    pending_queue = [r for r in reports if r["status"] != "Cleared"]

    if not pending_queue:
        st.success("All reported incidents have been cleared! No pending tickets in queue.")
        return

    st.markdown(
        f"""
        <div class="neu-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 600; color: #0F172A;">Active Queue Size: {len(pending_queue)} Sites</span>
                <span style="font-size: 0.8rem; color: #64748B;">Formula: Score = 0.35·S + 0.25·R + 0.20·W + 0.20·T</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Queue Table
    table_rows = []
    for idx, r in enumerate(pending_queue, start=1):
        table_rows.append([
            f"<strong>#{idx}</strong>",
            f"<span style='color:#2563EB; font-weight:600;'>{r['report_uid']}</span>",
            f"<strong>{r['ward_name']}</strong><br/><span style='font-size:0.75rem; color:#64748B;'>{r['address'][:40]}</span>",
            f"+{r.get('severity_component', 0):.1f}<br/>{severity_badge_html(r.get('severity_level'))}",
            f"+{r.get('recurrence_component', 0):.1f}",
            f"+{r.get('waste_type_component', 0):.1f}",
            f"+{r.get('waiting_time_component', 0):.1f}",
            f"<span class='prio-pill'>{r.get('priority_score', 0):.1f}</span>",
            status_badge_html(r['status'])
        ])

    from components.shared_ui import render_clean_table
    render_clean_table(
        headers=["Rank", "UID", "Ward & Landmark", "Severity (S)", "Recurrence (R)", "Hazard (W)", "Wait (T)", "Composite Score", "Status"],
        rows=table_rows
    )

    # Supervisory Priority Override (Feature 1 & RBAC)
    if has_permission("tune_weights"):
        st.markdown("### Supervisory Priority Score Override")
        with st.expander("Adjust Incident Priority (With Mandatory Civic Audit Log)"):
            with st.form("override_priority_form"):
                override_options = [f"{r['report_uid']} - {r['ward_name']} ({r.get('priority_score', 0):.1f})" for r in pending_queue]
                selected_override = st.selectbox("Select Ticket to Override", options=override_options)
                ov_uid = selected_override.split(" - ")[0]
                target_rep = next((r for r in pending_queue if r["report_uid"] == ov_uid), None)

                c1, c2 = st.columns([1, 2])
                with c1:
                    new_score = st.slider("New Priority Score", 0.0, 100.0, float(target_rep.get("priority_score", 50.0)), 0.5)
                with c2:
                    reason = st.text_input("Operational Reason for Override", placeholder="e.g. Dignitary VIP transit route / School reopening zone")

                submit_override = st.form_submit_button("Commit Score Override & Log Audit", type="primary")

            if submit_override and target_rep and reason:
                user = get_current_user()
                repo.set_priority_override(target_rep["id"], new_score, reason)
                repo.log_audit("PRIORITY_OVERRIDE", "Report", ov_uid, user["full_name"], user["id"], str(target_rep.get("priority_score")), str(new_score))
                st.success(f"Priority for {ov_uid} adjusted to {new_score:.1f}. Event recorded in immutable audit log.")
                st.rerun()
