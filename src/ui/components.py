"""
NIRMAAN AI - Reusable UI Components
Common widgets, breadcrumbs, status indicators, and notification cards.
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
            <div style="margin-bottom: 0.5rem;">
                <span style="font-size: 0.75rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">
                    NIRMAAN AI &rsaquo; {active_tab or 'Platform'}
                </span>
                <h1 style="font-size: 1.75rem; font-weight: 700; color: #0F172A; margin: 0.15rem 0 0.25rem 0;">
                    {title}
                </h1>
                <p style="font-size: 0.88rem; color: #475569; margin: 0;">
                    {subtitle}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div style="text-align: right; background: #FFFFFF; padding: 0.5rem 0.85rem; border-radius: 8px; border: 1px solid #E2E8F0; margin-top: 0.25rem;">
                <div style="font-size: 0.78rem; font-weight: 700; color: #0F172A;">{user['full_name']}</div>
                <div style="font-size: 0.72rem; color: #059669; font-weight: 600;">Role: {user['role']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div class="civic-notice">
            <strong>Civic Notice:</strong> {CIVIC_DISCLAIMER}
        </div>
        """,
        unsafe_allow_html=True
    )


def severity_badge_html(level: str) -> str:
    """Returns HTML markup for color-coded severity pills."""
    lvl = (level or "Medium").capitalize()
    if lvl == "High":
        return '<span class="badge badge-high">HIGH</span>'
    elif lvl == "Low":
        return '<span class="badge badge-low">LOW</span>'
    else:
        return '<span class="badge badge-med">MEDIUM</span>'


def status_badge_html(status: str) -> str:
    """Returns HTML markup for operational task status pills."""
    st_val = status or "Pending"
    if st_val == "Cleared":
        return '<span class="badge badge-cleared">CLEARED</span>'
    elif st_val == "Under Cleanup":
        return '<span class="badge badge-med">UNDER CLEANUP</span>'
    elif st_val == "Reopened":
        return '<span class="badge badge-high">REOPENED</span>'
    else:
        return '<span class="badge badge-pending">PENDING</span>'
