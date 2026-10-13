"""
NIRMAAN AI - Reusable UI Components
Common widgets, breadcrumbs, status indicators, and notification cards.
Ensures 100% contrast on both dark page backdrops and light card surfaces.
"""

import streamlit as st
from src.config import CIVIC_DISCLAIMER
from src.auth.rbac import get_current_user


def render_header(title: str, subtitle: str = "", active_tab: str = ""):
    """Renders consistent top application header with breadcrumbs and active user."""
    user = get_current_user()

    col1, col2 = st.columns([3, 1.2])
    with col1:
        st.markdown(
            f"""
            <div style="margin-bottom: 0.75rem;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #2DD4BF; text-transform: uppercase; letter-spacing: 0.08em;">
                    NIRMAAN AI &rsaquo; {active_tab or 'Platform'}
                </span>
                <h1 style="font-size: 1.85rem; font-weight: 800; color: #FFFFFF !important; margin: 0.2rem 0 0.35rem 0; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">
                    {title}
                </h1>
                <p style="font-size: 0.92rem; color: #CBD5E1 !important; margin: 0; line-height: 1.45;">
                    {subtitle}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div style="text-align: right; background: rgba(255, 255, 255, 0.98); padding: 0.6rem 0.95rem; border-radius: 10px; border: 1px solid #CBD5E1; margin-top: 0.25rem; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                <div style="font-size: 0.82rem; font-weight: 800; color: #0F172A;">{user['full_name']}</div>
                <div style="font-size: 0.74rem; color: #047857; font-weight: 700;">Role: {user['role']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div class="civic-notice">
            <strong style="color: #1E3A8A;">Civic Notice:</strong> <span style="color: #1E3A8A;">{CIVIC_DISCLAIMER}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def severity_badge_html(level: str) -> str:
    """Returns HTML markup for color-coded severity pills with high contrast."""
    lvl = (level or "Medium").capitalize()
    if lvl == "High":
        return '<span class="badge badge-high">HIGH</span>'
    elif lvl == "Low":
        return '<span class="badge badge-low">LOW</span>'
    else:
        return '<span class="badge badge-med">MEDIUM</span>'


def status_badge_html(status: str) -> str:
    """Returns HTML markup for operational task status pills with high contrast."""
    st_val = (status or "Pending").strip()
    if st_val in ["Cleared", "Verified Cleared", "Verified Closed"]:
        return '<span class="badge badge-cleared">VERIFIED CLEARED</span>'
    elif st_val == "Under Cleanup":
        return '<span class="badge badge-progress">UNDER CLEANUP</span>'
    elif st_val == "In Progress":
        return '<span class="badge badge-progress">IN PROGRESS</span>'
    elif st_val in ["Awaiting Verification", "Verification", "Under Verification"]:
        return '<span class="badge badge-verify">VERIFICATION</span>'
    elif st_val == "Assigned":
        return '<span class="badge badge-assigned">ASSIGNED</span>'
    elif st_val == "Blocked":
        return '<span class="badge badge-blocked">BLOCKED</span>'
    elif st_val == "Reopened":
        return '<span class="badge badge-reopened">REOPENED</span>'
    elif st_val in ["Under Review", "Prioritized"]:
        return '<span class="badge badge-pending">UNDER REVIEW</span>'
    else:
        return '<span class="badge badge-pending">PENDING</span>'
