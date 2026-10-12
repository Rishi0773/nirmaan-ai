"""
NIRMAAN AI - Overview Dashboard View
Presents database-backed civic metrics, severe pending cases,
and ward-level waste distributions.
"""

import streamlit as st
import pandas as pd
from src.database.repository import Repository
from src.ui.components import render_header, severity_badge_html, status_badge_html


def render(repo: Repository):
    render_header(
        title="Civic Overview & Operational Command",
        subtitle="Real-time monitoring of municipal waste reports, triage statuses, and active blackspots.",
        active_tab="Dashboard"
    )

    metrics = repo.get_dashboard_metrics()

    # 1. Top Metric Cards (Neumorphic Style)
    mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
    with mcol1:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: #2563EB;">
                <div class="metric-val">{metrics['total_reports']}</div>
                <div class="metric-lbl">Total Reports</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with mcol2:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: #DC2626;">
                <div class="metric-val">{metrics['high_severity_pending']}</div>
                <div class="metric-lbl">High-Severity Pending</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with mcol3:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: #D97706;">
                <div class="metric-val">{metrics['active_hotspots']}</div>
                <div class="metric-lbl">Active Hotspots</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with mcol4:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: #0284C7;">
                <div class="metric-val">{metrics['under_cleanup']}</div>
                <div class="metric-lbl">Under Cleanup</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with mcol5:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: #16A34A;">
                <div class="metric-val">{metrics['cleared_reports']}</div>
                <div class="metric-lbl">Verified Cleared</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 2. Urgent High-Priority Reports Table
    st.markdown("### Top Critical Garbage Hotspots Requiring Dispatch")
    all_reports = repo.get_all_reports()
    pending_high = [r for r in all_reports if r["status"] != "Cleared"][:6]

    if pending_high:
        table_rows = []
        for r in pending_high:
            rank_str = f"#{r.get('priority_rank', '-')}" if r.get('priority_rank') else "-"
            table_rows.append([
                f"<strong>{rank_str}</strong>",
                f"<span style='color:#2563EB; font-weight:600;'>{r['report_uid']}</span>",
                f"<strong>{r['ward_name']}</strong><br/><span style='font-size:0.75rem; color:#64748B;'>{r['address'][:45]}</span>",
                r['waste_category'].replace('_', ' ').title(),
                severity_badge_html(r.get('severity_level')),
                f"<span class='prio-pill'>{r.get('priority_score', 0):.1f}</span>",
                status_badge_html(r['status'])
            ])

        from components.shared_ui import render_clean_table
        render_clean_table(
            headers=["Rank", "UID", "Ward & Location", "Category", "Severity", "Priority Score", "Status"],
            rows=table_rows
        )
    else:
        st.info("No unresolved complaints in queue.")

    # 3. Charts: Ward-wise breakdown & Waste Categories
    st.markdown("### Operational Ward & Waste Breakdown")
    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.markdown("<strong>Incidents by Bengaluru Ward</strong>", unsafe_allow_html=True)
            if all_reports:
                ward_counts = pd.DataFrame(all_reports)["ward_name"].value_counts()
                st.bar_chart(ward_counts)

    with c2:
        with st.container(border=True):
            st.markdown("<strong>Waste Category Distribution</strong>", unsafe_allow_html=True)
            if all_reports:
                cat_counts = pd.DataFrame(all_reports)["waste_category"].value_counts()
                st.bar_chart(cat_counts)
