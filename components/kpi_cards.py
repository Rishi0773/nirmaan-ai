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
    """
    metrics = repo.get_dashboard_metrics()

    total_rep = metrics.get("total_reports", 0)
    high_pending = metrics.get("high_severity_pending", 0)
    active_hotspots = metrics.get("active_hotspots", 0)
    under_cleanup = metrics.get("under_cleanup", 0)
    verified_cleared = metrics.get("cleared_reports", 0)

    st.markdown(
        f"""
        <style>
        .kpi-strip-container {{
            display: grid !important;
            grid-template-columns: repeat(5, 1fr) !important;
            gap: 1rem !important;
            margin-top: 1.75rem !important;
            margin-bottom: 2rem !important;
            width: 100% !important;
        }}

        @media (max-width: 1024px) {{
            .kpi-strip-container {{
                grid-template-columns: repeat(3, 1fr) !important;
            }}
        }}

        @media (max-width: 640px) {{
            .kpi-strip-container {{
                grid-template-columns: 1fr !important;
            }}
        }}

        .kpi-glass-card {{
            background: rgba(255, 255, 255, 0.92) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(255, 255, 255, 0.85) !important;
            border-radius: 14px !important;
            padding: 1.15rem 1.25rem !important;
            box-shadow: 0 10px 25px rgba(5, 11, 26, 0.25) !important;
            position: relative !important;
            overflow: hidden !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }}

        .kpi-glass-card:hover {{
            transform: translateY(-3px) !important;
            box-shadow: 0 14px 32px rgba(5, 11, 26, 0.35) !important;
        }}

        .kpi-glass-card::before {{
            content: "" !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 5px !important;
            height: 100% !important;
        }}

        .kpi-c1::before {{ background: #2563EB !important; }}
        .kpi-c2::before {{ background: #DC2626 !important; }}
        .kpi-c3::before {{ background: #D97706 !important; }}
        .kpi-c4::before {{ background: #0284C7 !important; }}
        .kpi-c5::before {{ background: #16A34A !important; }}

        .kpi-card-val {{
            font-family: 'Space Grotesk', 'Plus Jakarta Sans', sans-serif !important;
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            color: #0F172A !important;
            line-height: 1.05 !important;
        }}

        .kpi-card-lbl {{
            font-size: 0.76rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            color: #475569 !important;
            margin-top: 0.4rem !important;
        }}
        </style>

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

