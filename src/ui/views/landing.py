"""
NIRMAAN AI - Landing & Academic Concept Overview
Presents the project problem statement, objectives, architecture,
and academic methodology as formulated in the college presentation.
"""

import streamlit as st
from src.ui.components import render_header


def render():
    render_header(
        title="NIRMAAN AI: Garbage Hotspot Prioritization",
        subtitle="Intelligent Civic Waste Prioritization & Geospatial Hotspot Analytics",
        active_tab="Project Overview"
    )

    st.markdown(
        """
        <div class="neu-card">
            <h3 style="margin-top: 0; color: #0F172A;">Executive Concept & Purpose</h3>
            <p style="color: #334155; line-height: 1.6;">
                <strong>NIRMAAN AI</strong> is an intelligent municipal decision-support system designed to resolve
                a critical limitation in urban grievance redressal: <em>First-Come-First-Served (FCFS) dispatching</em>.
                By combining <strong>YOLOv8 computer vision</strong>, <strong>OpenCV contour analysis</strong>,
                <strong>spatiotemporal DBSCAN clustering</strong>, and an <strong>explainable prioritization engine</strong>,
                the platform empowers civic sanitation authorities (such as BBMP) to address the most severe, chronic,
                and health-hazardous garbage sites first.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="neu-card" style="height: 100%;">
                <h4 style="color: #059669; margin-top: 0;">Presentation Objectives (Slide 3)</h4>
                <ol style="color: #334155; font-size: 0.9rem; line-height: 1.7; padding-left: 1.25rem;">
                    <li><strong>Computer Vision Triage:</strong> Detect and grade waste volume using YOLOv8 & OpenCV.</li>
                    <li><strong>Geotagged Storage:</strong> Securely persist timestamped reports and validated coordinates in SQLite.</li>
                    <li><strong>Hotspot Discovery:</strong> Aggregate repeat complaints into spatial clusters using DBSCAN.</li>
                    <li><strong>Explainable Prioritization:</strong> Rank dispatches balancing Severity, Recurrence, Hazard, and Waiting Time.</li>
                    <li><strong>Closed-Loop Operations:</strong> Track field cleanup tasks and verify outcomes using Before-and-After imagery.</li>
                    <li><strong>Rigorous Evaluation:</strong> Quantify dwell-time reduction against traditional FCFS queues.</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="neu-card" style="height: 100%;">
                <h4 style="color: #2563EB; margin-top: 0;">Core End-to-End Pipeline (Slide 4)</h4>
                <div style="font-size: 0.88rem; color: #334155; line-height: 1.8;">
                    <div style="background: #F8FAFC; padding: 0.4rem 0.75rem; border-radius: 6px; margin-bottom: 0.35rem; border: 1px solid #E2E8F0;">
                        1. Citizen files photo & GPS location
                    </div>
                    <div style="background: #F8FAFC; padding: 0.4rem 0.75rem; border-radius: 6px; margin-bottom: 0.35rem; border: 1px solid #E2E8F0;">
                        2. YOLOv8 & OpenCV compute objects & coverage %
                    </div>
                    <div style="background: #F8FAFC; padding: 0.4rem 0.75rem; border-radius: 6px; margin-bottom: 0.35rem; border: 1px solid #E2E8F0;">
                        3. Spatial aggregation flags repeat blackspots
                    </div>
                    <div style="background: #F8FAFC; padding: 0.4rem 0.75rem; border-radius: 6px; margin-bottom: 0.35rem; border: 1px solid #E2E8F0;">
                        4. Transparent formula computes Priority Score
                    </div>
                    <div style="background: #F8FAFC; padding: 0.4rem 0.75rem; border-radius: 6px; margin-bottom: 0.35rem; border: 1px solid #E2E8F0;">
                        5. Field team cleans site & submits Before/After proof
                    </div>
                    <div style="background: #F8FAFC; padding: 0.4rem 0.75rem; border-radius: 6px; border: 1px solid #E2E8F0;">
                        6. AI verification & supervisor approval closes ticket
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("### Technology Stack & Architecture (Slide 8 & 9)")

    tech_cols = st.columns(4)
    with tech_cols[0]:
        st.markdown(
            """
            <div class="neu-card" style="text-align: center;">
                <div style="font-size: 1.5rem;">🤖</div>
                <div style="font-weight: 700; color: #0F172A; margin-top: 0.25rem;">Vision & AI</div>
                <div style="font-size: 0.8rem; color: #64748B;">Ultralytics YOLOv8 & OpenCV Saliency</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with tech_cols[1]:
        st.markdown(
            """
            <div class="neu-card" style="text-align: center;">
                <div style="font-size: 1.5rem;">🗺️</div>
                <div style="font-weight: 700; color: #0F172A; margin-top: 0.25rem;">Geospatial</div>
                <div style="font-size: 0.8rem; color: #64748B;">Scikit-learn DBSCAN & Folium GIS</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with tech_cols[2]:
        st.markdown(
            """
            <div class="neu-card" style="text-align: center;">
                <div style="font-size: 1.5rem;">📊</div>
                <div style="font-weight: 700; color: #0F172A; margin-top: 0.25rem;">UI & Dashboard</div>
                <div style="font-size: 0.8rem; color: #64748B;">Streamlit with Neumorphic CSS</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with tech_cols[3]:
        st.markdown(
            """
            <div class="neu-card" style="text-align: center;">
                <div style="font-size: 1.5rem;">💾</div>
                <div style="font-weight: 700; color: #0F172A; margin-top: 0.25rem;">Data Persistence</div>
                <div style="font-size: 0.8rem; color: #64748B;">SQLite Relational WAL Storage</div>
            </div>
            """,
            unsafe_allow_html=True
        )
