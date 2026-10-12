"""
NIRMAAN AI - Analytics & Evaluation View
Simulates and quantifies the operational performance advantage of NIRMAAN
Priority Dispatching against baseline First-Come-First-Served (FCFS) queuing (PPT Slide 2 & 9).
"""

import streamlit as st
import pandas as pd
from src.database.repository import Repository
from src.engine.evaluation import evaluate_fcfs_vs_priority
from src.ui.components import render_header


def render(repo: Repository):
    render_header(
        title="Simulation Analytics: NIRMAAN vs. FCFS Queuing",
        subtitle="Empirical comparison showing how priority dispatching minimizes hazardous waste dwell time on streets.",
        active_tab="Evaluation"
    )

    st.markdown(
        """
        <div class="neu-card">
            <h4 style="margin-top: 0; color: #0F172A;">Evaluation Objective (Slide 2 & 9)</h4>
            <p style="font-size: 0.86rem; color: #334155; line-height: 1.6;">
                Traditional grievance redressal follows a strict <strong>First-Come-First-Served (FCFS)</strong> order,
                forcing high-density hazardous blackspots to wait while older minor litter complaints are serviced first.
                NIRMAAN dynamically promotes high-severity, chronic, and health-hazardous sites to the front of the queue.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Simulator Controls
    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        crew_count = st.slider("Active Sanitation Strike Crews", min_value=1, max_value=6, value=2)
    with ctrl_col2:
        daily_capacity = st.slider("Cleanup Tickets Serviced per Crew/Day", min_value=1, max_value=5, value=2)

    eval_data = evaluate_fcfs_vs_priority(repo, crews_count=crew_count, cleanups_per_crew_day=daily_capacity)

    if "error" in eval_data:
        st.warning(eval_data["error"])
        return

    # Metric Comparison Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: #DC2626;">
                <div class="metric-val">{eval_data['fcfs_high_wait_days']} Days</div>
                <div class="metric-lbl">FCFS High-Severity Wait Time</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: #059669;">
                <div class="metric-val">{eval_data['prio_high_wait_days']} Days</div>
                <div class="metric-lbl">NIRMAAN High-Severity Wait Time</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: #2563EB;">
                <div class="metric-val">-{eval_data['high_wait_reduction_pct']}%</div>
                <div class="metric-lbl">Critical Dwell Time Reduction</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Comparison Table
    st.markdown("### Waiting Time by Severity Category")
    st.table(eval_data["summary_table"])

    # Progression Chart
    st.markdown("### Cumulative Severity Cleared Over Dispatch Days")
    prog_df = eval_data["progression_df"].set_index("Day")
    st.line_chart(prog_df)
