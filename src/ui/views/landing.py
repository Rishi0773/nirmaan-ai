"""
NIRMAAN AI - Project Documentation & Civic Architecture (About Page)
Comprehensive technical documentation of the problem statement, computer vision pipeline,
spatiotemporal DBSCAN clustering, explainable priority scoring, and field verification workflow.
"""

import streamlit as st
from src.ui.components import render_header


def render():
    render_header(
        title="About NIRMAAN AI: Garbage Hotspot Prioritization",
        subtitle="An intelligent municipal decision-support system designed for dynamic urban solid waste triage.",
        active_tab="About NIRMAAN AI"
    )

    # 1. Executive Concept & Problem Statement
    st.markdown(
        """
        <div class="neu-card">
            <h3 style="margin-top: 0; color: #0F172A; font-size: 1.3rem;">
                1. Problem Statement: Moving Beyond First-Come-First-Served (FCFS) Triage
            </h3>
            <p style="color: #334155; line-height: 1.65; font-size: 0.95rem;">
                In major metropolitan centers such as Bengaluru, civic grievance redressal platforms historically
                process solid waste complaints on a strict <strong>First-Come-First-Served (FCFS)</strong> timeline.
                Under FCFS, an isolated piece of plastic litter reported at 08:00 AM takes scheduling precedence over a
                massive, rotting commercial food waste heap spilling across storm drains reported at 08:30 AM.
            </p>
            <p style="color: #334155; line-height: 1.65; font-size: 0.95rem;">
                This creates critical public health failures: chronic blackspots fester, disease vectors multiply,
                and sanitation strike crews lack data on where urgent interventions will yield the highest civic impact.
                <strong>NIRMAAN AI</strong> introduces an explainable, automated decision-support pipeline that analyzes
                visual accumulation severity, geographic recurrence patterns, waste hazard levels, and citizen waiting time.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Methodology & Core Pipeline Sections
    c1, c2 = st.columns(2, gap="medium")

    with c1:
        st.markdown(
            """
            <div class="neu-card" style="height: 100%;">
                <h4 style="color: #059669; margin-top: 0; font-size: 1.15rem;">
                    2. Computer Vision Waste Detection & Grading
                </h4>
                <p style="color: #334155; font-size: 0.9rem; line-height: 1.6;">
                    When a photograph is submitted, the vision pipeline performs dual-stage evaluation:
                </p>
                <ul style="color: #334155; font-size: 0.88rem; line-height: 1.7; padding-left: 1.2rem;">
                    <li><strong>Object Detection (YOLOv8):</strong> Identifies discrete waste items across classes including <em>plastics, paper/cardboard, organic kitchen waste, hazardous chemicals</em>, and <em>mixed street trash</em>.</li>
                    <li><strong>Ground Footprint Analysis (OpenCV):</strong> Uses adaptive color thresholding and contour segmentation to calculate the percentage of pavement or ground surface covered by waste debris.</li>
                    <li><strong>Severity Tiers:</strong> Synthesizes object counts and coverage into standard tiers (<strong>Low</strong>, <strong>Medium</strong>, <strong>High</strong>) with an explainable 0–100 Severity Score ($S$).</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            r"""
            <div class="neu-card" style="height: 100%;">
                <h4 style="color: #2563EB; margin-top: 0; font-size: 1.15rem;">
                    3. Spatiotemporal DBSCAN Clustering
                </h4>
                <p style="color: #334155; font-size: 0.9rem; line-height: 1.6;">
                    Rather than treating complaints as disconnected incidents, NIRMAAN aggregates reports across time and space:
                </p>
                <ul style="color: #334155; font-size: 0.88rem; line-height: 1.7; padding-left: 1.2rem;">
                    <li><strong>Density-Based Spatial Clustering:</strong> Runs Scikit-learn DBSCAN using the Haversine metric with a configured neighborhood radius ($\epsilon = 200\\text{ m}$).</li>
                    <li><strong>Chronic Hotspot Identification:</strong> When multiple independent incidents cluster within this buffer, the system flags the locus as an <em>Active Hotspot</em>.</li>
                    <li><strong>Recurrence Index ($R$):</strong> Quantifies repeat dumping frequency, penalizing chronic blackspots to trigger root-cause civic interventions and targeted surveillance.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    c3, c4 = st.columns(2, gap="medium")

    with c3:
        st.markdown(
            """
            <div class="neu-card" style="height: 100%;">
                <h4 style="color: #D97706; margin-top: 0; font-size: 1.15rem;">
                    4. Explainable Priority Scoring Engine
                </h4>
                <p style="color: #334155; font-size: 0.9rem; line-height: 1.6;">
                    Municipal decisions must remain transparent to officers and citizens. NIRMAAN uses a normalized 4-component index:
                </p>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.75rem; font-family: monospace; font-size: 0.85rem; color: #0F172A; margin-bottom: 0.75rem;">
                    Priority = 0.35·S + 0.25·R + 0.20·W + 0.20·T
                </div>
                <ul style="color: #334155; font-size: 0.85rem; line-height: 1.6; padding-left: 1.2rem;">
                    <li><strong>S (Severity, 35%):</strong> Evaluated accumulation volume and count.</li>
                    <li><strong>R (Recurrence, 25%):</strong> Cluster frequency within 200m buffer.</li>
                    <li><strong>W (Waste Hazard, 20%):</strong> Immediate penalty for biomedical or decomposing organic matter.</li>
                    <li><strong>T (Waiting Time, 20%):</strong> Starvation-prevention escalator preventing low-severity complaints from remaining neglected indefinitely.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            """
            <div class="neu-card" style="height: 100%;">
                <h4 style="color: #7C3AED; margin-top: 0; font-size: 1.15rem;">
                    5. Closed-Loop Field Operations & Verification
                </h4>
                <p style="color: #334155; font-size: 0.9rem; line-height: 1.6;">
                    Ticket dispatching is only half the battle; closing the redressal loop requires tamper-resistant verification:
                </p>
                <ul style="color: #334155; font-size: 0.85rem; line-height: 1.6; padding-left: 1.2rem;">
                    <li><strong>Operational Task Dispatch:</strong> Dispatches strike teams with clear location coordinates, landmark details, and waste classification.</li>
                    <li><strong>Before/After Proof:</strong> Field crews capture post-cleanup photos upon task execution.</li>
                    <li><strong>Automated AI Verification:</strong> OpenCV contour subtraction computes the net <em>waste reduction percentage</em> (target &ge; 70%).</li>
                    <li><strong>Supervisory Closure:</strong> Ward Officers inspect photographic proof and formally authorize ticket closure or order re-cleaning.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 3. Technology Stack Architecture
    st.markdown("### Technology Stack & Architecture")
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        st.markdown(
            """
            <div class="neu-card" style="text-align: center; height: 100%;">
                <div style="font-size: 1.6rem;">🤖</div>
                <div style="font-weight: 700; color: #0F172A; margin-top: 0.25rem;">Vision & AI</div>
                <div style="font-size: 0.8rem; color: #64748B;">Ultralytics YOLOv8 & OpenCV Contours</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t2:
        st.markdown(
            """
            <div class="neu-card" style="text-align: center; height: 100%;">
                <div style="font-size: 1.6rem;">🗺️</div>
                <div style="font-weight: 700; color: #0F172A; margin-top: 0.25rem;">Geospatial GIS</div>
                <div style="font-size: 0.8rem; color: #64748B;">Scikit-learn DBSCAN & Folium Leaflet</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t3:
        st.markdown(
            """
            <div class="neu-card" style="text-align: center; height: 100%;">
                <div style="font-size: 1.6rem;">💻</div>
                <div style="font-weight: 700; color: #0F172A; margin-top: 0.25rem;">UI & Operations</div>
                <div style="font-size: 0.8rem; color: #64748B;">Streamlit with Glassmorphic Design</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t4:
        st.markdown(
            """
            <div class="neu-card" style="text-align: center; height: 100%;">
                <div style="font-size: 1.6rem;">💾</div>
                <div style="font-weight: 700; color: #0F172A; margin-top: 0.25rem;">Data & Reports</div>
                <div style="font-size: 0.8rem; color: #64748B;">SQLite WAL & ReportLab Dossiers</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 4. Limitations & Academic Integrity Notice
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="neu-card" style="border-left: 4px solid #F59E0B;">
            <h4 style="margin-top: 0; color: #B45309;">System Scope, Assumptions & Limitations</h4>
            <div style="font-size: 0.88rem; color: #334155; line-height: 1.65;">
                <p>
                    <strong>Academic Research Prototype:</strong> NIRMAAN AI was built as an academic decision-support prototype.
                    While designed around Bengaluru municipal geographic coordinates and actual ward nomenclatures,
                    it is <em>not</em> an officially commissioned BBMP (Bruhat Bengaluru Mahanagara Palike) IT deployment.
                </p>
                <p>
                    <strong>Computer Vision Boundaries:</strong> Visual coverage ratio serves as a proxy for physical volume
                    but is sensitive to camera angles, lighting conditions, and obstructions. The model includes an OpenCV
                    saliency fallback engine to maintain continuous operational availability on systems without hardware GPUs.
                </p>
                <p>
                    <strong>Demonstration Data:</strong> Preloaded reports are generated as representative synthetic incident records
                    for benchmarking and algorithmic comparison against traditional FCFS triage queues.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
