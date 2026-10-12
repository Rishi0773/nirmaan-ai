"""
NIRMAAN AI - Municipal Presentation Reports & Export View
Generates downloadable CSV dumps and formatted PDF executive summaries
for municipal pilot proposals and academic evaluations (Feature 7).
"""

from pathlib import Path
import streamlit as st
from src.database.repository import Repository
from src.utils.reporting import export_reports_to_csv, generate_executive_pdf_report
from src.ui.components import render_header


def render(repo: Repository):
    render_header(
        title="Civic Reports & Executive Exports",
        subtitle="Export structured municipal data dumps and formal PDF dossiers for BBMP review presentations.",
        active_tab="Reporting & Exports"
    )

    reports = repo.get_all_reports()
    metrics = repo.get_dashboard_metrics()
    hotspots = repo.get_all_hotspots()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="neu-card">
                <h3 style="margin-top: 0; color: #0F172A; font-size: 1.2rem;">
                    Structured CSV Data Export
                </h3>
                <p style="font-size: 0.85rem; color: #64748B;">
                    Complete tabular dataset including ticket UIDs, coordinates, YOLO detection metrics,
                    severity grades, and priority scores.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        csv_path = export_reports_to_csv(reports, "nirmaan_reports_export.csv")
        with open(csv_path, "rb") as f:
            csv_bytes = f.read()

        st.download_button(
            label="Download Complete Reports CSV",
            data=csv_bytes,
            file_name="nirmaan_bengaluru_reports.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

    with col2:
        st.markdown(
            """
            <div class="neu-card">
                <h3 style="margin-top: 0; color: #0F172A; font-size: 1.2rem;">
                    Executive PDF Municipal Dossier
                </h3>
                <p style="font-size: 0.85rem; color: #64748B;">
                    Professionally styled ReportLab PDF containing KPI tables, active hotspot listings,
                    FCFS comparison summaries, and academic integrity notices.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Generate Executive PDF Dossier", use_container_width=True):
            pdf_path = generate_executive_pdf_report(metrics, hotspots, "nirmaan_pilot_executive_summary.pdf")
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                label="Download Generated PDF Dossier",
                data=pdf_bytes,
                file_name="nirmaan_executive_dossier.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
