"""
NIRMAAN AI - Single Professional Top Navigation Bar
Renders the single, full-width dark navy navbar with NIRMAAN AI branding on the left
and clean, icon-consistent navigation links horizontally on the right.
"""

import streamlit as st
from src.auth.rbac import get_current_user, ROLES, set_current_user
from src.database.repository import Repository


NAV_LINKS = [
    ("Home", "Home"),
    ("Report Garbage", "Report Garbage"),
    ("Live Map", "Live Map"),
    ("Track Report", "Track Report"),
    ("Hotspots", "Hotspots"),
    ("Analytics", "Analytics"),
    ("About", "About"),
    ("Login", "Login")
]


def render_navbar(repo: Repository):
    """Renders the single clean top navigation bar."""
    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = "Home"

    active_page = st.session_state.get("nav_page", "Home")
    user = get_current_user()

    # Outer container with border wrapper for isolated styling
    with st.container(border=True):
        st.markdown(
            """<div id="top-navbar-wrapper"></div>
<style>
div[data-testid="stVerticalBlockBorderWrapper"]:has(#top-navbar-wrapper) {
    background: rgba(8, 17, 39, 0.94) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
    padding: 0.5rem 1.25rem !important;
    margin-bottom: 1.25rem !important;
    box-shadow: 0 10px 25px rgba(5, 11, 26, 0.35) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(#top-navbar-wrapper) button {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #CBD5E1 !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 0.75rem !important;
    min-height: 36px !important;
    height: 36px !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
    white-space: nowrap !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(#top-navbar-wrapper) button:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    color: #FFFFFF !important;
    border-color: rgba(255, 255, 255, 0.15) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(#top-navbar-wrapper) button[kind="primary"] {
    background: rgba(20, 184, 166, 0.25) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(45, 212, 191, 0.5) !important;
    font-weight: 700 !important;
}
</style>""",
            unsafe_allow_html=True
        )

        # Single row layout: Brand on left, Nav links on right
        cols = st.columns([2.6, 0.8, 1.3, 0.9, 1.1, 0.9, 0.9, 0.8, 0.9])

        # Column 0: Logo & Title
        with cols[0]:
            st.markdown(
                """
                <div style="display:flex; align-items:center; gap:0.65rem; height:36px;">
                    <div style="width:30px; height:30px; border-radius:6px; background:linear-gradient(135deg, #0D9488 0%, #10B981 100%); display:flex; align-items:center; justify-content:center; color:#fff; font-weight:800; font-size:15px; box-shadow:0 0 10px rgba(16,185,129,0.45); flex-shrink:0;">
                        N
                    </div>
                    <div style="display:flex; flex-direction:column; line-height:1.15;">
                        <span style="font-size:1.05rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.02em;">NIRMAAN AI</span>
                        <span style="font-size:0.64rem; font-weight:600; text-transform:uppercase; letter-spacing:0.07em; color:#2DD4BF;">Garbage Hotspot Prioritization</span>
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
