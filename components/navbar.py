"""
NIRMAAN AI - Single Professional Top Navigation Bar
Renders the full-width dark navy navbar with NIRMAAN AI branding,
responsive navigation links, and active user role badge.
"""

import streamlit as st
from src.auth.rbac import get_current_user
from src.database.repository import Repository

NAV_LINKS = [
    ("Home", "Home"),
    ("Report Garbage", "Report Garbage"),
    ("Live Map", "Live Map"),
    ("Track Report", "Track Report"),
    ("Hotspots", "Hotspots"),
    ("Analytics", "Analytics"),
    ("About", "About"),
    ("Login", "Civic Portal")
]


def render_navbar(repo: Repository):
    """Renders the single clean top navigation bar."""
    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = "Home"

    active_page = st.session_state.get("nav_page", "Home")
    user = get_current_user()
    role = user.get("role", "Citizen")

    # Outer container with border wrapper for isolated styling
    with st.container(border=True):
        st.markdown("""<div id="top-navbar-wrapper"></div>""", unsafe_allow_html=True)

        # Single row layout: Brand on left, Nav links on right
        cols = st.columns([2.5, 0.7, 1.2, 0.9, 1.0, 0.9, 0.9, 0.7, 1.1])

        # Column 0: Logo & Title
        with cols[0]:
            role_badge_color = "#10B981" if role == "Administrator" else "#3B82F6" if role == "Ward Officer" else "#F59E0B" if role == "Sanitation Supervisor" else "#8B5CF6" if role == "Cleanup Worker" else "#06B6D4"
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:0.65rem; height:36px;">
                    <div style="width:30px; height:30px; border-radius:6px; background:linear-gradient(135deg, #0D9488 0%, #10B981 100%); display:flex; align-items:center; justify-content:center; color:#fff; font-weight:800; font-size:15px; box-shadow:0 0 10px rgba(16,185,129,0.45); flex-shrink:0;">
                        N
                    </div>
                    <div style="display:flex; flex-direction:column; line-height:1.15;">
                        <span style="font-size:1.05rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.02em;">NIRMAAN AI</span>
                        <span style="font-size:0.64rem; font-weight:600; text-transform:uppercase; letter-spacing:0.07em; color:#2DD4BF;">
                            {user.get('full_name', 'Civic Portal').split(' ')[0]} ({role})
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Navigation Links
        for idx, (page_key, label) in enumerate(NAV_LINKS, start=1):
            with cols[idx]:
                is_active = (active_page == page_key)
                btn_type = "primary" if is_active else "secondary"
                if st.button(label, key=f"navlink_{page_key}", use_container_width=True, type=btn_type):
                    st.session_state["nav_page"] = page_key
                    st.rerun()
