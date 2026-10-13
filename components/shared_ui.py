"""
NIRMAAN AI - Shared UI Utilities & Badges
Provides clean HTML rendering without markdown parsing defects,
high-contrast severity badges, and status indicators.
"""

import textwrap
import streamlit as st


def severity_badge(level: str) -> str:
    """Returns HTML for color-coded severity pills with high-contrast text."""
    lvl = (level or "Medium").capitalize()
    if lvl == "High":
        return '<span class="badge badge-high">HIGH</span>'
    elif lvl == "Low":
        return '<span class="badge badge-low">LOW</span>'
    else:
        return '<span class="badge badge-med">MEDIUM</span>'


def status_badge(status: str) -> str:
    """Returns HTML for operational task status pills with high-contrast text."""
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


def render_html_safely(html_content: str):
    """
    Renders HTML without CommonMark interpreting indented lines as code blocks.
    Uses st.html if supported, with textwrap.dedent fallback.
    """
    cleaned = textwrap.dedent(html_content).strip()
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


def render_clean_table(headers: list, rows: list, caption: str = ""):
    """
    Renders a styled, responsive table safely avoiding markdown indentation bugs.
    Ensures crisp dark text on white table background.
    """
    header_th = "".join([f"<th>{h}</th>" for h in headers])
    body_tr = ""
    for r in rows:
        cells = "".join([f"<td>{c}</td>" for c in r])
        body_tr += f"<tr>{cells}</tr>\n"

    table_markup = f"""
<div class="clean-table-card">
  {f'<div style="font-weight:800; color:#0F172A; margin-bottom:0.75rem; font-size:1.05rem;">{caption}</div>' if caption else ''}
  <table class="civic-table">
    <thead>
      <tr>{header_th}</tr>
    </thead>
    <tbody>
      {body_tr}
    </tbody>
  </table>
</div>
"""
    render_html_safely(table_markup)
