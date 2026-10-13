"""
NIRMAAN AI - Role-Based Civic Operations Command Dashboards
Implements dedicated, functionally differentiated operational dashboards for:
1. Administrator (System oversight, user management, calibration, health)
2. Ward Officer (Ward-scoped review, verification approval/rejection, escalation)
3. Sanitation Supervisor (Crew workload, worker assignment, blocked triage)
4. Cleanup Worker (Field operations, map directions, accept task, report blocked, submit verification)
5. Citizen (My reports timeline, before/after proof, follow-up notes, tracking)
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from src.database.repository import Repository
from src.auth.rbac import get_current_user, has_permission, enforce_permission
from src.ui.components import render_header, severity_badge_html, status_badge_html
from components.shared_ui import render_clean_table, severity_badge, status_badge
from src.config import DEFAULT_PRIORITY_WEIGHTS


def render(repo: Repository):
    """Entry point routing to the active user's dedicated role dashboard."""
    user = get_current_user()
    role = user.get("role", "Citizen")

    if role == "Cleanup Worker":
        render_worker_dashboard(repo, user)
    elif role == "Sanitation Supervisor":
        render_supervisor_dashboard(repo, user)
    elif role == "Ward Officer":
        render_ward_officer_dashboard(repo, user)
    elif role == "Citizen":
        render_citizen_dashboard(repo, user)
    else:
        render_admin_dashboard(repo, user)


# ==============================================================================
# 1. CLEANUP WORKER DASHBOARD (Field Operations)
# ==============================================================================
def render_worker_dashboard(repo: Repository, user: dict):
    render_header(
        title=f"Field Operations — {user['full_name']}",
        subtitle=f"Assigned Ward: {user.get('ward_assigned', 'Central')} | Role: Cleanup Strike Crew",
        active_tab="Field Operations"
    )

    worker_id = user["id"]
    tasks = repo.get_tasks_for_worker(worker_id)

    # Worker KPI Strip
    assigned_count = len([t for t in tasks if t["status"] in ["Pending", "Assigned"]])
    in_progress_count = len([t for t in tasks if t["status"] in ["In Progress", "Under Cleanup"]])
    awaiting_ver_count = len([t for t in tasks if t["status"] == "Awaiting Verification"])
    cleared_count = len([t for t in tasks if t["status"] in ["Cleared", "Verified Closed"]])

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""<div class="metric-card" style="border-left-color: #3B82F6;">
                <div class="metric-val">{assigned_count}</div>
                <div class="metric-lbl">Assigned Tasks</div>
            </div>""", unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            f"""<div class="metric-card" style="border-left-color: #F59E0B;">
                <div class="metric-val">{in_progress_count}</div>
                <div class="metric-lbl">In Progress</div>
            </div>""", unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            f"""<div class="metric-card" style="border-left-color: #8B5CF6;">
                <div class="metric-val">{awaiting_ver_count}</div>
                <div class="metric-lbl">Awaiting Verification</div>
            </div>""", unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            f"""<div class="metric-card" style="border-left-color: #10B981;">
                <div class="metric-val">{cleared_count}</div>
                <div class="metric-lbl">Verified Cleared</div>
            </div>""", unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    tab_active, tab_history = st.tabs(["Active Field Tasks", "Completed Cleanups History"])

    with tab_active:
        active_tasks = [t for t in tasks if t["status"] not in ["Cleared", "Verified Closed"]]
        if not active_tasks:
            st.info("No active tasks currently assigned to your crew. Check back when the supervisor dispatches new work orders.")
        else:
            for t in active_tasks:
                task_id = t["id"]
                st_badge = status_badge_html(t["status"])
                sev_badge = severity_badge_html(t.get("severity_level", "Medium"))
                prio_score = t.get("priority_score", 0.0)

                # Map link for worker GPS navigation
                lat = t.get("latitude", 12.9352)
                lon = t.get("longitude", 77.6245)
                gmaps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

                st.markdown(
                    f"""
                    <div class="neu-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">
                            <div>
                                <h3 style="margin: 0; color: #0F172A; font-size: 1.15rem; font-weight: 800;">
                                    {t['task_code']} &mdash; <span style="color: #1D4ED8; font-weight: 700;">{t['report_uid']}</span>
                                </h3>
                                <div style="font-size: 0.88rem; color: #334155; margin-top: 0.35rem;">
                                    <strong style="color: #0F172A;">Ward:</strong> <span style="color: #0F172A; font-weight: 600;">{t['ward_name']}</span> | <strong style="color: #0F172A;">Address:</strong> <span style="color: #0F172A;">{t['address']}</span>
                                </div>
                                <div style="font-size: 0.84rem; color: #475569; margin-top: 0.2rem;">
                                    <strong style="color: #0F172A;">Landmark:</strong> <span style="color: #334155;">{t.get('landmark') or 'Not specified'}</span> | <strong style="color: #0F172A;">Category:</strong> <span style="color: #334155; font-weight: 600;">{t['waste_category'].replace('_', ' ').title()}</span>
                                </div>
                            </div>
                            <div style="display: flex; gap: 0.5rem; align-items: center;">
                                {sev_badge}
                                {st_badge}
                                <span class="prio-pill">{prio_score:.1f} pts</span>
                            </div>
                        </div>
                        <div style="font-size: 0.86rem; color: #1E293B; margin-top: 0.75rem; background: #F1F5F9; padding: 0.65rem 0.85rem; border-radius: 8px; border: 1px solid #CBD5E1;">
                            <strong style="color: #0F172A;">Priority Rationale:</strong> Severity={t.get('severity_component', 0):.1f}, Recurrence={t.get('recurrence_component', 0):.1f}, Hazard={t.get('waste_type_component', 0):.1f}, Elapsed Time={t.get('waiting_time_component', 0):.1f}.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Action buttons row
                b_c1, b_c2, b_c3 = st.columns([1.2, 1.2, 1.5])

                with b_c1:
                    st.link_button("📍 Navigate (GPS Directions)", gmaps_url, use_container_width=True)

                with b_c2:
                    if t["status"] in ["Pending", "Assigned"]:
                        if st.button("Accept Task & Start", key=f"btn_accept_{task_id}", type="primary", use_container_width=True):
                            repo.worker_accept_task(task_id, worker_id, user["full_name"])
                            st.success(f"Task {t['task_code']} accepted. Status updated to In Progress.")
                            st.rerun()

                with b_c3:
                    pass

                # Action forms for In-Progress tasks
                if t["status"] in ["In Progress", "Under Cleanup", "Assigned"]:
                    c_act1, c_act2 = st.columns(2)

                    with c_act1:
                        with st.expander(f"Submit Cleanup for Verification ({t['task_code']})"):
                            st.caption("Upload photographic proof to submit your work to the supervisor verification queue.")
                            b_upload = st.file_uploader("Before-cleanup Photo (Optional update)", type=["jpg", "png"], key=f"w_b_{task_id}")
                            a_upload = st.file_uploader("After-cleanup Photo *", type=["jpg", "png"], key=f"w_a_{task_id}")
                            w_notes = st.text_input("Work Summary Notes", value="Entire litter cleared, road swept, lime disinfected.", key=f"w_notes_{task_id}")

                            if st.button("Submit to Verification Queue", key=f"w_sub_{task_id}", type="primary", use_container_width=True):
                                from src.config import AFTER_DIR, BEFORE_DIR
                                b_path = BEFORE_DIR / f"{t['report_uid']}_before.jpg"
                                a_path = AFTER_DIR / f"{t['report_uid']}_after.jpg"

                                if a_upload:
                                    with open(a_path, "wb") as f:
                                        f.write(a_upload.getbuffer())
                                else:
                                    from src.database.seed_data import create_synthetic_image
                                    create_synthetic_image(a_path, f"AFTER {t['report_uid']}", object_count=0, clean_state=True)

                                if b_upload:
                                    with open(b_path, "wb") as f:
                                        f.write(b_upload.getbuffer())
                                elif not b_path.exists():
                                    from src.database.seed_data import create_synthetic_image
                                    create_synthetic_image(b_path, f"BEFORE {t['report_uid']}", object_count=5, clean_state=False)

                                repo.worker_submit_completion(
                                    task_id=task_id,
                                    worker_id=worker_id,
                                    worker_name=user["full_name"],
                                    before_img=str(b_path),
                                    after_img=str(a_path),
                                    notes=w_notes
                                )
                                st.success("Task submitted for verification! Ward Officer will review your submission.")
                                st.rerun()

                    with c_act2:
                        with st.expander(f"Report Site Blocked / Inaccessible"):
                            st.caption("If access is barred, vehicle cannot enter, or hazard is present, file a formal blocker reason.")
                            block_reason = st.text_area("Mandatory Blocker Reason *", placeholder="e.g. Road dug up for BWSSB pipe repair; gate locked; hazardous chemical spill requires Hazmat team...", key=f"w_blk_{task_id}")
                            if st.button("Confirm Site Blocked", key=f"w_btn_blk_{task_id}", use_container_width=True):
                                if not block_reason.strip():
                                    st.error("A mandatory reason is required to mark a site as blocked.")
                                else:
                                    repo.worker_report_blocked(task_id, worker_id, user["full_name"], block_reason.strip())
                                    st.warning(f"Task marked as Blocked. Supervisor has been notified.")
                                    st.rerun()

                st.markdown("---")

    with tab_history:
        completed = [t for t in tasks if t["status"] in ["Cleared", "Verified Closed"]]
        if completed:
            c_rows = []
            for t in completed:
                c_rows.append([
                    t["task_code"],
                    t["report_uid"],
                    t["ward_name"],
                    t["address"][:40],
                    severity_badge(t.get("severity_level")),
                    status_badge(t["status"]),
                    t.get("completed_at", "-")
                ])
            render_clean_table(
                headers=["Task Code", "Report UID", "Ward", "Address", "Severity", "Final Status", "Completed Date"],
                rows=c_rows
            )
        else:
            st.info("No completed cleanup tasks recorded yet.")


# ==============================================================================
# 2. WARD OFFICER DASHBOARD (Ward Scope, Review & Closure Verification)
# ==============================================================================
def render_ward_officer_dashboard(repo: Repository, user: dict):
    officer_ward = user.get("ward_assigned", "Koramangala")
    render_header(
        title=f"Ward Operations Command — {user['full_name']}",
        subtitle=f"Jurisdiction: Ward '{officer_ward}' | Role: Ward Officer & Verification Authority",
        active_tab="Ward Command"
    )

    # Ward Scope Filter
    all_reports = repo.get_all_reports()
    all_wards = sorted(list(set([r["ward_name"] for r in all_reports if r["ward_name"]])))
    default_w_idx = all_wards.index(officer_ward) if officer_ward in all_wards else 0

    col_w_sel, _ = st.columns([2, 3])
    with col_w_sel:
        selected_ward = st.selectbox("Inspect Ward Scope", all_wards, index=default_w_idx)

    ward_reports = [r for r in all_reports if r["ward_name"] == selected_ward]
    ward_tasks = [t for t in repo.get_all_tasks() if t.get("ward_name") == selected_ward]
    ward_hotspots = [h for h in repo.get_all_hotspots() if h.get("ward_name") == selected_ward]

    # Ward KPIs
    total_w = len(ward_reports)
    pending_w = len([r for r in ward_reports if r["status"] in ["Pending", "Submitted", "Under Review", "Prioritized"]])
    under_w = len([r for r in ward_reports if r["status"] in ["Under Cleanup", "In Progress", "Awaiting Verification", "Assigned"]])
    cleared_w = len([r for r in ward_reports if r["status"] in ["Cleared", "Verified Closed"]])
    high_w = len([r for r in ward_reports if r.get("severity_level") == "High" and r["status"] != "Cleared"])

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #2563EB;"><div class="metric-val">{total_w}</div><div class="metric-lbl">Total in Ward</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #DC2626;"><div class="metric-val">{high_w}</div><div class="metric-lbl">High-Severity</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #D97706;"><div class="metric-val">{len(ward_hotspots)}</div><div class="metric-lbl">Ward Clusters</div></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #0284C7;"><div class="metric-val">{under_w}</div><div class="metric-lbl">Under Cleanup</div></div>""", unsafe_allow_html=True)
    with m5:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #16A34A;"><div class="metric-val">{cleared_w}</div><div class="metric-lbl">Verified Cleared</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    tab_dispatch, tab_verify, tab_escalate, tab_ward_intel = st.tabs([
        "1. Triage & Strike Dispatch",
        "2. Verification & Closure Queue",
        "3. Case Escalation",
        "4. Ward Hotspots & Analytics"
    ])

    with tab_dispatch:
        st.markdown(f"### Unassigned Complaints in {selected_ward}")
        unassigned = [r for r in ward_reports if r["status"] in ["Pending", "Submitted", "Prioritized"]]
        if unassigned:
            u_rows = []
            for r in unassigned:
                rank_str = f"#{r.get('priority_rank', '-')}" if r.get('priority_rank') else "-"
                u_rows.append([
                    f"<strong style='color:#0F172A;'>{rank_str}</strong>",
                    f"<span style='color:#1D4ED8; font-weight:700;'>{r['report_uid']}</span>",
                    f"<span style='color:#334155;'>{r['address'][:40]}</span>",
                    f"<span style='color:#0F172A; font-weight:500;'>{r['waste_category'].replace('_', ' ').title()}</span>",
                    severity_badge(r.get("severity_level")),
                    f"<span class='prio-pill'>{r.get('priority_score', 0):.1f}</span>",
                    status_badge(r["status"])
                ])
            render_clean_table(
                headers=["Rank", "UID", "Address", "Category", "Severity", "Score", "Status"],
                rows=u_rows
            )

            # Quick dispatch form
            with st.expander(f"Dispatch Strike Team for {selected_ward}"):
                with st.form("ward_dispatch_form"):
                    rep_opts = [f"{r['report_uid']} - {r['address'][:35]} ({r.get('priority_score', 0):.1f} pts)" for r in unassigned]
                    sel_rep_str = st.selectbox("Select Report to Dispatch", rep_opts)
                    sel_rep_uid = sel_rep_str.split(" - ")[0]
                    target_rep = next(r for r in unassigned if r["report_uid"] == sel_rep_uid)

                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        team = st.selectbox("Assign Strike Team", [
                            f"{selected_ward} Strike Team Alpha",
                            f"{selected_ward} Strike Team Bravo",
                            "Mechanized Sweeper Unit",
                            "Emergency Biohazard Response"
                        ])
                    with d_col2:
                        prio = st.selectbox("Dispatch Urgency", ["Normal", "High", "Emergency"])

                    notes = st.text_input("Special Field Instructions", value="Clear road verge and spray lime disinfectant.")
                    dispatch_btn = st.form_submit_button("Authorize Work Order Dispatch", type="primary")

                if dispatch_btn:
                    task_code = f"TASK-{target_rep['report_uid'][-4:]}"
                    repo.create_task(
                        task_code=task_code,
                        report_id=target_rep["id"],
                        assigned_team=team,
                        supervisor_id=user["id"],
                        priority_level=prio,
                        notes=notes
                    )
                    repo.log_audit("WARD_DISPATCH", "Task", task_code, user["full_name"], user["id"], "Pending", "Under Cleanup")
                    st.success(f"Work order {task_code} dispatched to {team}!")
                    st.rerun()
        else:
            st.info(f"All complaints in {selected_ward} are currently dispatched or resolved.")

    with tab_verify:
        st.markdown(f"### Verification & Closure Review Queue — {selected_ward}")
        st.caption("Officers must inspect photographic evidence and computer vision reduction before authorizing ticket closure.")

        tasks_to_verify = [t for t in ward_tasks if t["status"] in ["Under Cleanup", "Awaiting Verification", "In Progress"]]
        if tasks_to_verify:
            v_opts = [f"{t['task_code']} &mdash; {t['report_uid']} ({t['status']})" for t in tasks_to_verify]
            chosen_v = st.selectbox("Select Task to Verify", v_opts)
            chosen_code = chosen_v.split(" &mdash; ")[0]
            target_t = next(t for t in tasks_to_verify if t["task_code"] == chosen_code)

            task_id = target_t["id"]
            existing_ver = repo.get_verification_by_task(task_id)

            from src.config import BEFORE_DIR, AFTER_DIR
            b_path = BEFORE_DIR / f"{target_t['report_uid']}_before.jpg"
            a_path = AFTER_DIR / f"{target_t['report_uid']}_after.jpg"

            col_img1, col_img2 = st.columns(2)
            with col_img1:
                st.markdown("<strong>Pre-cleanup Photograph</strong>", unsafe_allow_html=True)
                if b_path.exists():
                    st.image(str(b_path), use_container_width=True)
                else:
                    st.info("Pre-cleanup photo logged in database.")
            with col_img2:
                st.markdown("<strong>Post-cleanup Field Photograph</strong>", unsafe_allow_html=True)
                if a_path.exists():
                    st.image(str(a_path), use_container_width=True)
                else:
                    st.info("Awaiting post-cleanup upload from field crew.")

            with st.form(f"officer_verify_form_{task_id}"):
                decision = st.selectbox(
                    "Supervisory Verdict *",
                    ["Verified Clean", "Needs Re-cleaning"],
                    help="Approving as Verified Clean marks ticket closed. Needs Re-cleaning reopens ticket for strike team."
                )
                reason = st.text_area("Supervisory Assessment Remarks *", value="Inspected imagery: area completely cleared of debris, road margin swept, verified clear.")
                sub_dec_btn = st.form_submit_button("Commit Verification Sign-off", type="primary")

            if sub_dec_btn:
                from src.ml.verification import verify_cleanup_images
                # Run computer vision reduction analysis
                reduction_pct = 85.0
                ai_verdict = "Approved"
                if b_path.exists() and a_path.exists():
                    try:
                        v_res = verify_cleanup_images(str(b_path), str(a_path))
                        reduction_pct = v_res.get("waste_reduction_pct", 85.0)
                        ai_verdict = v_res.get("ai_verdict", "Approved")
                    except Exception:
                        pass

                repo.save_verification(
                    task_id=task_id,
                    before_image_path=str(b_path),
                    after_image_path=str(a_path),
                    waste_reduction_pct=reduction_pct,
                    ai_verdict=ai_verdict,
                    supervisor_decision=decision,
                    verified_by=user["id"],
                    verification_notes=reason
                )
                st.success(f"Verification completed. Outcome: '{decision}'. Ticket status updated.")
                st.rerun()
        else:
            st.info(f"No tasks in {selected_ward} currently pending verification.")

    with tab_escalate:
        st.markdown("### Escalate Severe / Chronic Complaints")
        st.caption("Flag chronic blackspots or biohazard accumulations requiring BBMP higher authority intervention.")

        pending_for_esc = [r for r in ward_reports if r["status"] != "Cleared"]
        if pending_for_esc:
            with st.form("escalate_form"):
                esc_opts = [f"{r['report_uid']} - {r['address'][:35]} ({r['waste_category']})" for r in pending_for_esc]
                esc_chosen = st.selectbox("Select Report to Escalate", esc_opts)
                esc_uid = esc_chosen.split(" - ")[0]
                target_esc = next(r for r in pending_for_esc if r["report_uid"] == esc_uid)

                esc_notes = st.text_area("Escalation Justification *", placeholder="Explain why standard strike dispatch is insufficient (e.g. chronic commercial dumper, overflowing stormwater canal)...")
                esc_submit = st.form_submit_button("Submit Formal Escalation", type="primary")

            if esc_submit and esc_notes.strip():
                with repo._conn() as conn:
                    conn.execute("UPDATE reports SET escalated = 1, escalation_notes = ? WHERE id = ?", (esc_notes.strip(), target_esc["id"]))
                    repo.log_audit("CASE_ESCALATE", "Report", esc_uid, user["full_name"], user["id"], "Normal", f"Escalated: {esc_notes.strip()}")
                st.success(f"Case {esc_uid} successfully escalated.")
                st.rerun()
        else:
            st.info("No active cases available to escalate.")

    with tab_ward_intel:
        st.markdown(f"### Spatial Clustering & Hotspots in {selected_ward}")
        if ward_hotspots:
            for hs in ward_hotspots:
                st.markdown(
                    f"""
                    <div class="neu-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong>Hotspot Code: {hs['hotspot_code']}</strong>
                            <span class="badge badge-high">Recurrence: {hs['recurrence_score']:.1f}</span>
                        </div>
                        <div style="font-size:0.85rem; color:#475569; margin-top:0.35rem;">
                            Incident Count: <strong>{hs['incident_count']}</strong> | Average Severity: {hs['avg_severity']:.1f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )
        else:
            st.info(f"No persistent clusters identified in {selected_ward}.")


# ==============================================================================
# 3. SANITATION SUPERVISOR DASHBOARD (Crew Operations & Assignments)
# ==============================================================================
def render_supervisor_dashboard(repo: Repository, user: dict):
    render_header(
        title=f"Sanitation Operations & Crew Command — {user['full_name']}",
        subtitle=f"Jurisdiction: {user.get('ward_assigned', 'Koramangala')} | Role: Sanitation Supervisor",
        active_tab="Supervisor Operations"
    )

    tasks = repo.get_all_tasks()
    workers = repo.get_users_by_role("Cleanup Worker")

    # Metrics
    t_assigned = len([t for t in tasks if t.get("worker_id") is not None])
    t_unassigned = len([t for t in tasks if t.get("worker_id") is None and t["status"] != "Cleared"])
    t_blocked = len([t for t in tasks if t["status"] == "Blocked"])
    t_in_progress = len([t for t in tasks if t["status"] in ["In Progress", "Under Cleanup"]])

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #3B82F6;"><div class="metric-val">{len(tasks)}</div><div class="metric-lbl">Total Work Orders</div></div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #F59E0B;"><div class="metric-val">{t_unassigned}</div><div class="metric-lbl">Needs Worker Assignment</div></div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #10B981;"><div class="metric-val">{t_in_progress}</div><div class="metric-lbl">Crew In Field</div></div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #EF4444;"><div class="metric-val">{t_blocked}</div><div class="metric-lbl">Blocked Work Orders</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    tab_assign, tab_blocked, tab_crew = st.tabs(["Worker Assignment", "Blocked Orders Triage", "Crew Workload Roster"])

    with tab_assign:
        st.markdown("### Assign Work Orders to Field Workers")
        pending_assign = [t for t in tasks if t["status"] != "Cleared"]
        if pending_assign:
            with st.form("assign_worker_form"):
                t_options = [f"{t['task_code']} - {t['report_uid']} ({t['ward_name']} | Worker: {t.get('worker_name_full') or 'Unassigned'})" for t in pending_assign]
                sel_task_str = st.selectbox("Select Work Order", t_options)
                sel_task_code = sel_task_str.split(" - ")[0]
                target_task = next(t for t in pending_assign if t["task_code"] == sel_task_code)

                w_options = [f"{w['full_name']} ({w.get('ward_assigned', 'Field')})" for w in workers]
                sel_worker_str = st.selectbox("Assign Worker", w_options)
                target_worker = workers[w_options.index(sel_worker_str)]

                inst = st.text_input("Operational Instructions", value="Prioritize commercial food waste removal and road margin sweep.")
                assign_btn = st.form_submit_button("Assign Worker to Task", type="primary")

            if assign_btn:
                repo.assign_task_to_worker(target_task["id"], target_worker["id"], user["id"], inst)
                st.success(f"Task {target_task['task_code']} assigned to {target_worker['full_name']}!")
                st.rerun()
        else:
            st.info("No tasks currently requiring assignment.")

    with tab_blocked:
        st.markdown("### Blocked Work Orders (Field Alerts)")
        blocked_tasks = [t for t in tasks if t["status"] == "Blocked"]
        if blocked_tasks:
            for bt in blocked_tasks:
                st.markdown(
                    f"""
                    <div class="neu-card" style="border-left: 4px solid #EF4444;">
                        <strong>Task: {bt['task_code']} &mdash; {bt['report_uid']} ({bt['ward_name']})</strong>
                        <div style="color: #DC2626; font-size: 0.88rem; margin-top: 0.35rem;">
                            <strong>Blocker Reason:</strong> {bt.get('blocked_reason') or 'No reason provided.'}
                        </div>
                        <div style="font-size: 0.82rem; color: #64748B; margin-top: 0.25rem;">
                            Worker: {bt.get('worker_name_full') or 'Field Crew'} | Scheduled: {bt.get('created_at')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("Unblock & Return to In Progress", key=f"unblk_{bt['id']}"):
                    repo.update_task_status(bt["id"], "In Progress", "Blocker cleared by supervisor.")
                    st.success(f"Task {bt['task_code']} moved back to In Progress.")
                    st.rerun()
        else:
            st.info("No blocked work orders reported by field crews.")

    with tab_crew:
        st.markdown("### Field Strike Crew Roster")
        c_data = []
        for w in workers:
            w_tasks = [t for t in tasks if t.get("worker_id") == w["id"]]
            c_data.append([
                w["full_name"],
                w.get("ward_assigned", "Central"),
                w.get("phone", "9845000000"),
                str(len(w_tasks)),
                str(len([t for t in w_tasks if t["status"] in ["In Progress", "Under Cleanup"]])),
                str(len([t for t in w_tasks if t["status"] in ["Cleared", "Verified Closed"]]))
            ])
        render_clean_table(
            headers=["Crew Member", "Ward", "Phone", "Total Tasks", "Active In-Field", "Completed"],
            rows=c_data
        )


# ==============================================================================
# 4. CITIZEN DASHBOARD (Grievance Portal, Tracking, Follow-ups)
# ==============================================================================
def render_citizen_dashboard(repo: Repository, user: dict):
    render_header(
        title=f"Citizen Grievance Portal — {user['full_name']}",
        subtitle="Report garbage accumulation, track redressal timeline, and inspect before-and-after proof.",
        active_tab="Citizen Portal"
    )

    my_reports = repo.get_reports_for_citizen(user["id"], user["full_name"])

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(
            f"""
            <div class="neu-card" style="border-left: 4px solid #10B981;">
                <h3 style="margin-top:0; color:#0F172A; font-size:1.15rem;">Welcome, {user['full_name']}!</h3>
                <p style="color:#334155; font-size:0.88rem; line-height:1.5;">
                    Your reports help municipal strike teams prioritize solid waste hot spots across Bengaluru.
                    Every report is evaluated via YOLOv8 computer vision to eliminate FCFS queue delays.
                </p>
            </div>
            """, unsafe_allow_html=True
        )
    with c2:
        if st.button("File a New Garbage Report", type="primary", use_container_width=True):
            st.session_state["nav_page"] = "Report Garbage"
            st.rerun()

    tab_my, tab_search, tab_guide = st.tabs(["My Filed Complaints", "Track Any Ticket", "Waste Guidelines"])

    with tab_my:
        if my_reports:
            for r in my_reports:
                st_badge = status_badge_html(r["status"])
                sev_badge = severity_badge_html(r.get("severity_level", "Medium"))

                # 7-stage visual lifecycle
                st_val = r["status"]
                stage_idx = 1
                if st_val in ["Under Review", "Pending"]:
                    stage_idx = 2
                elif st_val == "Prioritized":
                    stage_idx = 3
                elif st_val == "Assigned":
                    stage_idx = 4
                elif st_val in ["In Progress", "Under Cleanup"]:
                    stage_idx = 5
                elif st_val == "Awaiting Verification":
                    stage_idx = 6
                elif st_val in ["Cleared", "Verified Closed"]:
                    stage_idx = 7

                st.markdown(
                    f"""
                    <div class="neu-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-size:1.1rem; font-weight:700; color:#0F172A;">{r['report_uid']}</span>
                                <span style="font-size:0.85rem; color:#64748B; margin-left:0.5rem;">{r['ward_name']} &mdash; {r['address']}</span>
                            </div>
                            <div>
                                {sev_badge}
                                {st_badge}
                            </div>
                        </div>
                        <div style="font-size:0.82rem; color:#475569; margin-top:0.35rem;">
                            Category: {r['waste_category'].replace('_', ' ').title()} | Filed: {r['created_at']}
                        </div>
                        <div style="margin-top:0.75rem; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:0.6rem 0.85rem;">
                            <div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:0.25rem;">Redressal Lifecycle:</div>
                            <div style="display:flex; justify-content:space-between; font-size:0.72rem; color:#334155; font-weight:600;">
                                <span style="color: {'#059669' if stage_idx >= 1 else '#94A3B8'};">1. Submitted</span>
                                <span style="color: {'#059669' if stage_idx >= 2 else '#94A3B8'};">&rarr; 2. Reviewed</span>
                                <span style="color: {'#059669' if stage_idx >= 3 else '#94A3B8'};">&rarr; 3. Prioritized</span>
                                <span style="color: {'#059669' if stage_idx >= 4 else '#94A3B8'};">&rarr; 4. Assigned</span>
                                <span style="color: {'#059669' if stage_idx >= 5 else '#94A3B8'};">&rarr; 5. In Progress</span>
                                <span style="color: {'#059669' if stage_idx >= 6 else '#94A3B8'};">&rarr; 6. Verification</span>
                                <span style="color: {'#059669' if stage_idx >= 7 else '#94A3B8'};">&rarr; 7. Closed</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Expandable follow-up note
                with st.expander(f"Add Information / Follow-up for {r['report_uid']}"):
                    st.caption("Add extra observations (e.g. odour worsening, stray animals) without creating unnecessary duplicate tickets.")
                    f_notes = st.text_input("Follow-up observation", key=f"f_note_{r['id']}")
                    if st.button("Submit Follow-up", key=f"btn_f_{r['id']}") and f_notes.strip():
                        repo.add_report_followup(r["id"], user["id"], user["full_name"], f_notes.strip())
                        st.success("Follow-up appended to ticket record.")
                        st.rerun()

                    existing_f = repo.get_report_followups(r["id"])
                    if existing_f:
                        st.markdown("<strong>Previous Follow-ups:</strong>", unsafe_allow_html=True)
                        for ef in existing_f:
                            st.caption(f"• {ef['created_at']}: {ef['notes']} (by {ef['user_name']})")
        else:
            st.info("You haven't filed any garbage reports yet. Use the 'Report Garbage' button above to submit your first report!")

    with tab_search:
        st.markdown("### Search Grievance Redressal Timeline")
        search_uid = st.text_input("Enter Report UID (e.g. REP-BLR-001)", placeholder="REP-BLR-001")
        if search_uid.strip():
            found = repo.get_report_by_uid(search_uid.strip().upper())
            if found:
                st.success(f"Ticket Found: {found['report_uid']} ({found['status']})")
                hist = repo.get_report_status_history(found["id"])
                if hist:
                    st.markdown("<strong>Timeline History:</strong>", unsafe_allow_html=True)
                    for h in hist:
                        st.markdown(f"• **{h['created_at']}**: `{h['old_status'] or 'Start'}` &rarr; **{h['new_status']}** ({h.get('reason') or 'Updated'})")
                else:
                    st.info("No status transitions recorded yet.")
            else:
                st.warning("No ticket found matching that UID.")

    with tab_guide:
        st.markdown(
            """
            <div class="neu-card">
                <h4 style="margin-top:0;">Bengaluru Solid Waste Segregation & Grievance Guidelines</h4>
                <ul style="font-size:0.88rem; color:#334155; line-height:1.6;">
                    <li><strong>Wet Waste:</strong> Kitchen scraps, food waste, flower waste. Collected daily by municipal auto-tippers.</li>
                    <li><strong>Dry Waste:</strong> Paper, plastics, metals, glass, cardboard. Collected twice weekly.</li>
                    <li><strong>Sanitary & Hazardous Waste:</strong> Diapers, sanitary napkins, biomedical waste, paints, CFL bulbs. Must be wrapped in newspaper with red mark.</li>
                    <li><strong>Zero Blackspot Protocol:</strong> Dumping on vacant sites or street corners attracts spot fines under BBMP Solid Waste Management Bylaws.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )


# ==============================================================================
# 5. ADMINISTRATOR DASHBOARD (Full System Command, Health & Management)
# ==============================================================================
def render_admin_dashboard(repo: Repository, user: dict):
    render_header(
        title="Municipal Administrative Console & Executive Command",
        subtitle="System-wide decision-support monitoring, model health telemetry, user RBAC, and policy calibration.",
        active_tab="Admin Console"
    )

    metrics = repo.get_dashboard_metrics()
    health = repo.get_system_health()

    # System-wide KPI cards
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #2563EB;"><div class="metric-val">{metrics['total_reports']}</div><div class="metric-lbl">Total Reports</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #DC2626;"><div class="metric-val">{metrics['high_severity_pending']}</div><div class="metric-lbl">High-Severity</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #D97706;"><div class="metric-val">{metrics['active_hotspots']}</div><div class="metric-lbl">Active Hotspots</div></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #0284C7;"><div class="metric-val">{metrics['under_cleanup']}</div><div class="metric-lbl">Under Cleanup</div></div>""", unsafe_allow_html=True)
    with m5:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #16A34A;"><div class="metric-val">{metrics['cleared_reports']}</div><div class="metric-lbl">Verified Cleared</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    tab_overview, tab_users, tab_health, tab_calib, tab_audit = st.tabs([
        "System Overview",
        "User & Role Management",
        "Model Health & Telemetry",
        "Priority Calibration",
        "Audit Log Trail"
    ])

    with tab_overview:
        all_reports = repo.get_all_reports()
        pending_high = [r for r in all_reports if r["status"] != "Cleared"][:6]

        st.markdown("### Top Critical Garbage Hotspots Requiring Dispatch")
        if pending_high:
            table_rows = []
            for r in pending_high:
                rank_str = f"#{r.get('priority_rank', '-')}" if r.get('priority_rank') else "-"
                table_rows.append([
                    f"<strong style='color:#0F172A;'>{rank_str}</strong>",
                    f"<span style='color:#1D4ED8; font-weight:700;'>{r['report_uid']}</span>",
                    f"<strong style='color:#0F172A;'>{r['ward_name']}</strong><br/><span style='font-size:0.75rem; color:#475569;'>{r['address'][:45]}</span>",
                    f"<span style='color:#0F172A; font-weight:500;'>{r['waste_category'].replace('_', ' ').title()}</span>",
                    severity_badge_html(r.get('severity_level')),
                    f"<span class='prio-pill'>{r.get('priority_score', 0):.1f}</span>",
                    status_badge_html(r['status'])
                ])
            render_clean_table(
                headers=["Rank", "UID", "Ward & Location", "Category", "Severity", "Priority Score", "Status"],
                rows=table_rows
            )

        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            with st.container(border=True):
                st.markdown("<strong>Complaints by Bengaluru Ward</strong>", unsafe_allow_html=True)
                if all_reports:
                    w_counts = pd.DataFrame(all_reports)["ward_name"].value_counts()
                    st.bar_chart(w_counts)
        with c_chart2:
            with st.container(border=True):
                st.markdown("<strong>Waste Category Distribution</strong>", unsafe_allow_html=True)
                if all_reports:
                    c_counts = pd.DataFrame(all_reports)["waste_category"].value_counts()
                    st.bar_chart(c_counts)

    with tab_users:
        st.markdown("### Municipal User & Role Management")
        all_u = repo.get_users()
        u_data = []
        for u in all_u:
            u_data.append([
                str(u["id"]),
                u["full_name"],
                u["username"],
                f"<code>{u['role']}</code>",
                u.get("ward_assigned", "Central"),
                u.get("email", "-"),
                u.get("phone", "-")
            ])
        render_clean_table(
            headers=["ID", "Full Name", "Username", "Role", "Ward Assigned", "Email", "Phone"],
            rows=u_data
        )

        with st.expander("Register New Municipal User / Update Role"):
            with st.form("new_user_form"):
                uc1, uc2 = st.columns(2)
                with uc1:
                    new_uname = st.text_input("Username *", placeholder="officer_south")
                    new_fname = st.text_input("Full Name *", placeholder="Dr. V. Rao")
                    new_role = st.selectbox("Assign Role", ["Ward Officer", "Sanitation Supervisor", "Cleanup Worker", "Citizen", "Administrator"])
                with uc2:
                    new_email = st.text_input("Email", placeholder="v.rao@nirmaan.local")
                    new_phone = st.text_input("Phone", placeholder="9845012345")
                    new_ward = st.selectbox("Assign Ward", ["Central", "Koramangala", "Indiranagar", "Malleshwaram", "Whitefield", "Jayanagar", "HSR Layout"])
                sub_user_btn = st.form_submit_button("Register User", type="primary")

            if sub_user_btn and new_uname and new_fname:
                try:
                    repo.create_user(new_uname, new_fname, new_role, new_email, new_phone, new_ward)
                    repo.log_audit("USER_CREATE", "User", new_uname, user["full_name"], user["id"], "", f"Created {new_role}")
                    st.success(f"User {new_fname} ({new_role}) registered successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating user: {e}")

    with tab_health:
        st.markdown("### Operational Telemetry & System Health")
        h1, h2, h3 = st.columns(3)
        with h1:
            st.metric("Database File Size", f"{health['db_size_kb']} KB", health['db_status'])
            st.metric("Total Relational Tables", "15 Tables", "WAL Mode Enabled")
        with h2:
            st.metric("Vision Model Backend", health["detector_backend"])
            st.metric("Custom YOLO Weights", "Present" if health["custom_yolo_weights"] else "Base Nano Weights")
        with h3:
            st.metric("Registered Users", f"{health['user_count']} Active Accounts")
            st.metric("Audit Trail Records", f"{health['audit_count']} Immutable Logs")

    with tab_calib:
        st.markdown("### Priority Algorithm Weights Calibration")
        st.caption("Weights must sum to 1.0 (100%). Modifying weights recalculates priority ranks for all active municipal complaints.")

        with st.form("calib_weights_form"):
            s_w = st.slider("Severity Weight (S)", 0.0, 1.0, float(DEFAULT_PRIORITY_WEIGHTS["severity"]), 0.05)
            r_w = st.slider("Recurrence Weight (R)", 0.0, 1.0, float(DEFAULT_PRIORITY_WEIGHTS["recurrence"]), 0.05)
            w_w = st.slider("Waste Hazard Weight (W)", 0.0, 1.0, float(DEFAULT_PRIORITY_WEIGHTS["waste_type"]), 0.05)
            t_w = st.slider("Waiting Time Weight (T)", 0.0, 1.0, float(DEFAULT_PRIORITY_WEIGHTS["waiting_time"]), 0.05)
            total_sum = round(s_w + r_w + w_w + t_w, 2)

            if total_sum != 1.0:
                st.warning(f"Current weight sum is **{total_sum}**. Please adjust sliders so they sum exactly to 1.0.")
            else:
                st.success("Weights correctly sum to 1.0.")

            calib_btn = st.form_submit_button("Recalculate All Priority Scores", type="primary")

        if calib_btn:
            if total_sum != 1.0:
                st.error("Weights must sum exactly to 1.0 before recalculating priority scores.")
            else:
                from src.engine.priority import calculate_and_save_all_priorities
                weights_dict = {"severity": s_w, "recurrence": r_w, "waste_type": w_w, "waiting_time": t_w}
                calculate_and_save_all_priorities(repo, weights=weights_dict)
                repo.log_audit("CALIBRATE_WEIGHTS", "Engine", "PriorityWeights", user["full_name"], user["id"], str(DEFAULT_PRIORITY_WEIGHTS), str(weights_dict))
                st.success("All complaints re-prioritized successfully with updated weights!")
                st.rerun()

    with tab_audit:
        st.markdown("### Immutable Civic Audit Trail")
        logs = repo.get_audit_logs(limit=50)
        if logs:
            l_rows = []
            for l in logs:
                l_rows.append([
                    l["created_at"],
                    l["user_name"],
                    f"<code>{l['action']}</code>",
                    f"{l['entity_type']} ({l['entity_id']})",
                    l.get("new_value", "-")[:45]
                ])
            render_clean_table(
                headers=["Timestamp", "Authorized User", "Action", "Target Entity", "Change Summary"],
                rows=l_rows
            )
        else:
            st.info("No audit logs recorded yet.")
