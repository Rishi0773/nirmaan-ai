"""
NIRMAAN AI - Cleanup Task Operations View
Tracks field crew assignments, operational statuses (Pending, Under Cleanup, Cleared, Reopened),
and dispatches sanitation strike teams (PPT Slide 3 & 8).
"""

import streamlit as st
from src.database.repository import Repository
from src.ui.components import render_header, severity_badge_html, status_badge_html
from src.auth.rbac import has_permission, get_current_user


def render(repo: Repository):
    render_header(
        title="Sanitation Strike Team Operations",
        subtitle="Manage field crew assignments, scheduled work orders, and operational status transitions.",
        active_tab="Task Management"
    )

    tasks = repo.get_all_tasks()

    # 1. Filter and Create Controls
    c1, c2 = st.columns([3, 1])
    with c1:
        task_status_filter = st.selectbox("Filter Task Status", ["All", "Pending", "Under Cleanup", "Cleared", "Reopened"])
    with c2:
        pass

    filtered_tasks = [t for t in tasks if task_status_filter == "All" or t["status"] == task_status_filter]

    # 2. Existing Tasks List
    if filtered_tasks:
        for t in filtered_tasks:
            st.markdown(
                f"""
                <div class="neu-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin: 0; color: #0F172A; font-size: 1.15rem;">
                                {t['task_code']} &mdash; {t['report_uid']} ({t['ward_name']})
                            </h3>
                            <span style="font-size: 0.8rem; color: #64748B;">
                                Assigned Team: <strong>{t['assigned_team']}</strong> | Supervisor: {t.get('supervisor_name_full') or 'Ward Officer'}
                            </span>
                        </div>
                        <div>
                            {status_badge_html(t['status'])}
                        </div>
                    </div>
                    <div style="font-size: 0.85rem; color: #334155; margin-top: 0.5rem;">
                        <strong>Location:</strong> {t['address']}
                    </div>
                    <div style="font-size: 0.82rem; color: #64748B; margin-top: 0.25rem;">
                        Scheduled: {t['created_at']} | Notes: {t['notes'] or 'No special instructions.'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Operational Update Form per Task
            if has_permission("manage_tasks"):
                with st.expander(f"Update Status for {t['task_code']}"):
                    with st.form(f"update_task_{t['id']}"):
                        new_st = st.selectbox("Update Operational Status", ["Under Cleanup", "Cleared", "Reopened"], index=0)
                        notes = st.text_input("Operational Notes", value=t.get("notes", ""))
                        btn_update = st.form_submit_button("Commit Status Update", type="primary")

                    if btn_update:
                        user = get_current_user()
                        repo.update_task_status(t["id"], new_st, notes)
                        repo.log_audit("TASK_STATUS_UPDATE", "Task", t["task_code"], user["full_name"], user["id"], t["status"], new_st)
                        st.success(f"Task {t['task_code']} moved to {new_st}.")
                        st.rerun()
    else:
        st.info("No tasks found matching the selected status filter.")

    # 3. Create Task from Unassigned Reports
    if has_permission("manage_tasks"):
        st.markdown("### Dispatch New Cleanup Task")
        reports = repo.get_all_reports()
        pending_reports = [r for r in reports if r["status"] == "Pending"]

        if pending_reports:
            with st.form("create_new_task_form"):
                r_options = [f"{r['report_uid']} - {r['ward_name']} ({r.get('priority_score', 0):.1f} pts)" for r in pending_reports]
                selected_r = st.selectbox("Select Pending Report", options=r_options)
                selected_uid = selected_r.split(" - ")[0]
                target_report = next((r for r in pending_reports if r["report_uid"] == selected_uid), None)

                col_a, col_b = st.columns(2)
                with col_a:
                    assigned_team = st.selectbox("Assign Sanitation Team", [
                        "Ward Strike Team Alpha",
                        "Ward Strike Team Bravo",
                        "Mechanized Sweeper Unit 01",
                        "Drainage Desilting Gang"
                    ])
                with col_b:
                    prio_level = st.selectbox("Task Priority", ["High", "Normal", "Emergency"])

                task_notes = st.text_input("Dispatch Notes / Instructions", value="Clear road verge and lime-spray area.")
                dispatch_btn = st.form_submit_button("Dispatch Task to Field Crew", type="primary")

            if dispatch_btn and target_report:
                user = get_current_user()
                task_code = f"TASK-{target_report['report_uid'][-4:]}"
                repo.create_task(
                    task_code=task_code,
                    report_id=target_report["id"],
                    assigned_team=assigned_team,
                    supervisor_id=user["id"],
                    priority_level=prio_level,
                    notes=task_notes
                )
                repo.log_audit("TASK_DISPATCH", "Task", task_code, user["full_name"], user["id"], "Pending", "Under Cleanup")
                st.success(f"Task {task_code} dispatched to {assigned_team}!")
                st.rerun()
        else:
            st.info("No unassigned pending reports currently waiting for task dispatch.")
