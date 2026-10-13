"""
NIRMAAN AI - KPI Strip Component
Renders the 5 bottom translucent cards populated strictly from live SQLite database queries.
"""

import streamlit as st
from src.database.repository import Repository


def render_kpi_strip(repo: Repository):
    """
    Renders 5 translucent KPI cards:
    1. Total Reports
    2. High-Severity Pending
    3. Active Hotspots
    4. Under Cleanup
    5. Verified Cleared
    Populated directly from live database metrics.
    """
    metrics = repo.get_dashboard_metrics()

    total_rep = metrics.get("total_reports", 0)
    high_pending = metrics.get("high_severity_pending", 0)
    active_hotspots = metrics.get("active_hotspots", 0)
    under_cleanup = metrics.get("under_cleanup", 0)
    verified_cleared = metrics.get("cleared_reports", 0)

    st.markdown(
        f"""
        <div class="kpi-strip-container">
          <div class="kpi-glass-card kpi-c1">
            <div class="kpi-card-val">{total_rep}</div>
            <div class="kpi-card-lbl">Total Reports</div>
          </div>
          <div class="kpi-glass-card kpi-c2">
            <div class="kpi-card-val">{high_pending}</div>
            <div class="kpi-card-lbl">High-Severity Pending</div>
          </div>
          <div class="kpi-glass-card kpi-c3">
            <div class="kpi-card-val">{active_hotspots}</div>
            <div class="kpi-card-lbl">Active Hotspots</div>
          </div>
          <div class="kpi-glass-card kpi-c4">
            <div class="kpi-card-val">{under_cleanup}</div>
            <div class="kpi-card-lbl">Under Cleanup</div>
          </div>
          <div class="kpi-glass-card kpi-c5">
            <div class="kpi-card-val">{verified_cleared}</div>
            <div class="kpi-card-lbl">Verified Cleared</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
