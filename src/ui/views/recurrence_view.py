"""
NIRMAAN AI - Recurrence & Spatiotemporal Analysis View
Inspects empirical repeat dumping intervals and chronicles chronic blackspots.
Adheres strictly to academic honesty: clearly states baseline limitations (Feature 2).
"""

import streamlit as st
from src.database.repository import Repository
from src.ml.recurrence import analyze_hotspot_recurrence
from src.ui.components import render_header


def render(repo: Repository):
    render_header(
        title="Recurrence Analytics & Spatiotemporal Frequency",
        subtitle="Empirical tracking of repeat dumping intervals to identify chronic municipal blackspots.",
        active_tab="Recurrence Intelligence"
    )

    st.markdown(
        """
        <div class="neu-card">
            <h4 style="margin-top: 0; color: #0F172A;">Academic Integrity Notice on Recurrence Modeling</h4>
            <p style="font-size: 0.85rem; color: #334155; line-height: 1.6;">
                The recurrence risk indices below are derived from <strong>observed historical report intervals</strong>
                and spatial cluster density. In strict adherence to scientific ethics, NIRMAAN AI does not fabricate
                hypothetical machine learning predictions without longitudinal ground-truth datasets.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    hotspots = repo.get_all_hotspots()
    if not hotspots:
        st.info("No spatial clusters available for recurrence modeling.")
        return

    for hs in hotspots:
        reports = repo.get_hotspot_reports(hs["id"])
        analysis = analyze_hotspot_recurrence(reports)

        st.markdown(
            f"""
            <div class="neu-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #0F172A; font-size: 1.15rem;">
                        Cluster: {hs['hotspot_code']} ({hs['ward_name']})
                    </h3>
                    <span style="font-size: 0.8rem; font-weight: 700; color: #DC2626; background: #FEE2E2; padding: 0.25rem 0.65rem; border-radius: 9999px;">
                        Risk: {analysis['recurrence_risk_level']}
                    </span>
                </div>
                <div style="display: flex; gap: 2rem; margin-top: 0.75rem; font-size: 0.84rem; color: #334155;">
                    <div>Observed Repeat Tickets: <strong>{analysis['repeat_count']}</strong></div>
                    <div>Average Interval: <strong>{analysis['avg_interval_days'] if analysis['avg_interval_days'] else 'N/A'} days</strong></div>
                    <div>Recurrence Score: <strong>{analysis['recurrence_index']}/100</strong></div>
                </div>
                <p style="font-size: 0.82rem; color: #475569; margin-top: 0.5rem;">
                    <strong>Observation:</strong> {analysis['rationale']}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
