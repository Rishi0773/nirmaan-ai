"""
NIRMAAN AI - Hotspot Intelligence View
Spatial clustering intelligence via DBSCAN: tracks recurring dumping blackspots,
geographical cluster centroids, buffer radii, and historical frequency (PPT Slide 3 & 6).
"""

import streamlit as st
from src.database.repository import Repository
from src.ml.clustering import run_hotspot_clustering
from src.ui.components import render_header, severity_badge_html, status_badge_html
from src.auth.rbac import has_permission


def render(repo: Repository):
    render_header(
        title="Hotspot Intelligence & Spatial Clustering",
        subtitle="Unsupervised DBSCAN spatial aggregation identifying chronic dumping zones and blackspot spread.",
        active_tab="Hotspot Intelligence"
    )

    hotspots = repo.get_all_hotspots()

    # Re-run clustering trigger
    col_hdr1, col_hdr2 = st.columns([3, 1])
    with col_hdr1:
        st.markdown(
            f"""
            <div style="font-size: 0.9rem; color: #475569; margin-bottom: 0.5rem;">
                Currently tracking <strong>{len(hotspots)} active spatial clusters</strong> across Bengaluru.
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_hdr2:
        if has_permission("manage_tasks"):
            if st.button("Re-run DBSCAN Clustering", type="primary", use_container_width=True):
                with st.spinner("Clustering coordinates using Haversine metric (200m radius)..."):
                    res = run_hotspot_clustering(repo)
                    st.success(f"DBSCAN identified {len(res)} clusters.")
                    st.rerun()

    if not hotspots:
        st.info("No spatial clusters currently formed. Submit additional reports to trigger DBSCAN clustering.")
        return

    # Hotspot Cards
    for hs in hotspots:
        hs_reports = repo.get_hotspot_reports(hs["id"])

        st.markdown(
            f"""
            <div class="neu-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="margin: 0; color: #0F172A; font-size: 1.25rem;">
                            {hs['hotspot_code']} — {hs['ward_name']} Ward
                        </h3>
                        <span style="font-size: 0.8rem; color: #64748B;">
                            Centroid: ({hs['centroid_lat']:.4f}, {hs['centroid_lon']:.4f}) | Spread Radius: {hs['radius_meters']}m
                        </span>
                    </div>
                    <div>
                        <span style="font-size: 0.82rem; font-weight: 700; background: #FEE2E2; color: #DC2626; padding: 0.35rem 0.75rem; border-radius: 9999px;">
                            Recurrence Score: {hs['recurrence_score']:.1f}
                        </span>
                    </div>
                </div>
                <div style="display: flex; gap: 2rem; margin-top: 0.75rem; font-size: 0.85rem; color: #334155;">
                    <div>Logged Repeat Complaints: <strong>{hs['incident_count']}</strong></div>
                    <div>Average Cluster Severity: <strong>{hs['avg_severity']:.1f}/100</strong></div>
                    <div>Cluster Status: <strong>{hs['status']}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander(f"View {len(hs_reports)} Linked Reports in Cluster {hs['hotspot_code']}"):
            for hr in hs_reports:
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: space-between; padding: 0.4rem 0; border-bottom: 1px solid #F1F5F9; font-size: 0.84rem;">
                        <div>
                            <strong>{hr['report_uid']}</strong> — {hr['address'][:50]}
                            <span style="color: #64748B; font-size: 0.78rem;">({hr['created_at']})</span>
                        </div>
                        <div>
                            {severity_badge_html(hr.get('severity_level'))}
                            {status_badge_html(hr['status'])}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
