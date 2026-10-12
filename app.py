"""
NIRMAAN AI: Garbage Hotspot Prioritization
Clean Government Decision-Support Portal Entry Point
"""

import streamlit as st
from pathlib import Path

# Streamlit Page Configuration
st.set_page_config(
    page_title="NIRMAAN AI — Garbage Hotspot Prioritization",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from src.config import DB_PATH
from src.database.connection import init_db
from src.database.repository import Repository
from src.database.seed_data import seed_database
from src.ui.styles import apply_theme
from src.auth.rbac import get_current_user, set_current_user, ROLE_PERMISSIONS

# Import Components
from components.navbar import render_navbar
from components.hero import render_hero
from components.kpi_cards import render_kpi_strip
from components.shared_ui import render_clean_table, severity_badge, status_badge

# Ensure DB exists
if not DB_PATH.exists():
    init_db()
    seed_database()

repo = Repository()

# Inject Modern Theme Styling
apply_theme()

# Navigation State
if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "Home"

active_page = st.session_state.get("nav_page", "Home")
current_user = get_current_user()

# On public landing page and general pages, completely hide the Streamlit sidebar
# to ensure ONE single professional navigation system matching the reference design.
if active_page != "Admin Console":
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        button[data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Render Single Professional Full-Width Top Navbar
render_navbar(repo)

# ==============================================================================
# Page Routing
# ==============================================================================
if active_page == "Home":
    # 1. Main Wide Dominant Hero with Photo Backdrop, Search & Civic Assistant
    render_hero(repo)

    # 2. Bottom KPI Strip (5 Translucent Cards)
    render_kpi_strip(repo)

    # 3. Urgent Action Hotspots Table
    st.markdown(
        """
        <h3 style="color: #FFFFFF; font-weight: 800; font-size: 1.4rem; margin-top: 1.75rem; margin-bottom: 0.85rem; text-shadow: 0 2px 6px rgba(0,0,0,0.6);">
            Top Critical Garbage Hotspots Requiring Dispatch
        </h3>
        """,
        unsafe_allow_html=True
    )
    all_reports = repo.get_all_reports()
    pending_high = [r for r in all_reports if r["status"] != "Cleared"][:5]

    if pending_high:
        table_rows = []
        for r in pending_high:
            rank_str = f"#{r.get('priority_rank', '-')}" if r.get('priority_rank') else "-"
            table_rows.append([
                f"<strong>{rank_str}</strong>",
                f"<span style='color:#2563EB; font-weight:600;'>{r['report_uid']}</span>",
                f"<strong>{r['ward_name']}</strong><br/><span style='font-size:0.75rem; color:#64748B;'>{r['address'][:45]}</span>",
                r['waste_category'].replace('_', ' ').title(),
                severity_badge(r.get('severity_level')),
                f"<span class='prio-pill'>{r.get('priority_score', 0):.1f}</span>",
                status_badge(r['status'])
            ])

        render_clean_table(
            headers=["Rank", "UID", "Ward & Location", "Category", "Severity", "Priority Score", "Status"],
            rows=table_rows
        )

        b_c1, b_c2, b_c3 = st.columns(3)
        with b_c1:
            if st.button("Explore Live Hotspot Map", key="h_btn_map", use_container_width=True):
                st.session_state["nav_page"] = "Live Map"
                st.rerun()
        with b_c2:
            if st.button("File Incident Report", key="h_btn_rep", use_container_width=True):
                st.session_state["nav_page"] = "Report Garbage"
                st.rerun()
        with b_c3:
            if st.button("Municipal Civic Dashboard", key="h_btn_dash", use_container_width=True):
                st.session_state["nav_page"] = "Analytics"
                st.rerun()

elif active_page == "Report Garbage":
    from src.ui.views.report_incident import render
    render(repo)
elif active_page == "Live Map":
    from src.ui.views.map_view import render
    render(repo)
elif active_page == "Track Report":
    from src.ui.views.incident_details import render
    render(repo)
elif active_page == "Hotspots":
    from src.ui.views.hotspot_intel import render
    render(repo)
elif active_page == "Analytics":
    from src.ui.views.dashboard import render
    render(repo)
elif active_page == "About":
    from src.ui.views.landing import render
    render()
elif active_page == "Login" or active_page == "Admin Console":
    st.markdown("## Civic Operations & Role Management")
    st.caption("Access authenticated municipal tools, switch simulated identity, and manage fieldwork operations.")

    adm_col1, adm_col2 = st.columns([1.2, 2])
    with adm_col1:
        with st.container(border=True):
            st.markdown(f"**Current Identity:** {current_user['full_name']}")
            st.markdown(f"**Role:** `{current_user['role']}`")
            st.markdown(f"**Ward:** {current_user.get('ward_assigned', 'Central')}")

            all_users = repo.get_users()
            user_opts = [f"{u['full_name']} ({u['role']})" for u in all_users]
            curr_idx = 0
            for i, u in enumerate(all_users):
                if u["username"] == current_user["username"]:
                    curr_idx = i
                    break
            chosen = st.selectbox("Switch Simulated Identity", user_opts, index=curr_idx)
            if st.button("Confirm Role Switch", type="primary", use_container_width=True):
                target = all_users[user_opts.index(chosen)]
                set_current_user(target)
                st.success(f"Switched identity to {target['full_name']} ({target['role']}).")
                st.rerun()

    with adm_col2:
        with st.container(border=True):
            st.markdown("### Municipal Operations Console")
            op_c1, op_c2 = st.columns(2)
            with op_c1:
                if st.button("Priority Queue", use_container_width=True):
                    st.session_state["nav_page"] = "Priority Queue"
                    st.rerun()
                if st.button("Task Operations", use_container_width=True):
                    st.session_state["nav_page"] = "Operations"
                    st.rerun()
                if st.button("Verification Review", use_container_width=True):
                    st.session_state["nav_page"] = "Verification"
                    st.rerun()
                if st.button("Recurrence Analysis", use_container_width=True):
                    st.session_state["nav_page"] = "Recurrence"
                    st.rerun()
            with op_c2:
                if st.button("Evaluation (NIRMAAN vs FCFS)", use_container_width=True):
                    st.session_state["nav_page"] = "Evaluation"
                    st.rerun()
                if st.button("Municipal PDF & CSV Exports", use_container_width=True):
                    st.session_state["nav_page"] = "Exports"
                    st.rerun()
                if st.button("Immutable Civic Audit Trail", use_container_width=True):
                    st.session_state["nav_page"] = "Audit Trail"
                    st.rerun()
                if st.button("Calibration & Settings", use_container_width=True):
                    st.session_state["nav_page"] = "Settings"
                    st.rerun()

elif active_page == "Priority Queue":
    from src.ui.views.priority_queue import render
    render(repo)
elif active_page == "Operations":
    from src.ui.views.task_management import render
    render(repo)
elif active_page == "Verification":
    from src.ui.views.verification_view import render
    render(repo)
elif active_page == "Recurrence":
    from src.ui.views.recurrence_view import render
    render(repo)
elif active_page == "Evaluation":
    from src.ui.views.analytics_eval import render
    render(repo)
elif active_page == "Exports":
    from src.ui.views.reports_export import render
    render(repo)
elif active_page == "Audit Trail":
    from src.ui.views.audit_logs import render
    render(repo)
elif active_page == "Settings":
    from src.ui.views.settings_view import render
    render(repo)
