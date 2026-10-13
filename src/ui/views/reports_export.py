"""
NIRMAAN AI - Municipal Presentation Reports & Export View
Generates downloadable CSV dumps and formatted PDF executive summaries
for municipal pilot proposals and academic evaluations.
"""

from pathlib import Path
import streamlit as st
from src.database.repository import Repository
from src.utils.reporting import (
    export_reports_to_csv, generate_executive_pdf_report,
    generate_incident_pdf_report, generate_ward_operations_pdf_report
)
from src.ui.components import render_header
from src.auth.rbac import has_permission, get_current_user


def render(repo: Repository):
    render_header(
        title="Civic Reports & Executive Exports",
        subtitle="Export structured municipal data dumps, incident dossiers, and formal PDF dossiers.",
        active_tab="Reporting & Exports"
    )

    user = get_current_user()
    reports = repo.get_all_reports()
    metrics = repo.get_dashboard_metrics()
    hotspots = repo.get_all_hotspots()
    wards = sorted(list(set([r["ward_name"] for r in reports if r["ward_name"]])))

    tab_pdf, tab_csv = st.tabs(["Formal PDF Dossiers", "Tabular CSV Data Exports"])

    with tab_pdf:
        p_col1, p_col2 = st.columns(2)

        with p_col1:
            st.markdown(
                """
                <div class="neu-card">
                    <h3 style="margin-top: 0; color: #0F172A; font-size: 1.15rem;">
                        Executive Pilot Assessment Dossier
                    </h3>
                    <p style="font-size: 0.85rem; color: #64748B;">
                        Complete ReportLab PDF containing KPI summaries, top recurring hotspots,
                        FCFS comparison analysis, and academic integrity disclaimers.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            try:
                exec_pdf_path = generate_executive_pdf_report(metrics, hotspots, "nirmaan_executive_dossier.pdf")
                with open(exec_pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                st.download_button(
                    label="Download Executive PDF Dossier",
                    data=pdf_bytes,
                    file_name="nirmaan_executive_summary.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating executive PDF: {e}")

        with p_col2:
            st.markdown(
                """
                <div class="neu-card">
                    <h3 style="margin-top: 0; color: #0F172A; font-size: 1.15rem;">
                        Ward Operations Dossier
                    </h3>
                    <p style="font-size: 0.85rem; color: #64748B;">
                        Ward-level breakdown of incident counts, pending strikes, resolution statuses,
                        and local blackspot distribution.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            chosen_ward = st.selectbox("Select Ward for PDF Export", wards, index=0)
            ward_reps = [r for r in reports if r["ward_name"] == chosen_ward]

            try:
                ward_pdf_path = generate_ward_operations_pdf_report(chosen_ward, ward_reps, f"nirmaan_ward_{chosen_ward}.pdf")
                with open(ward_pdf_path, "rb") as f:
                    w_bytes = f.read()

                st.download_button(
                    label=f"Download {chosen_ward} Ward PDF Dossier",
                    data=w_bytes,
                    file_name=f"nirmaan_ward_{chosen_ward}_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating ward PDF: {e}")

        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

        with st.expander("Generate Single Incident Investigation PDF"):
            if reports:
                r_opts = [f"{r['report_uid']} - {r['ward_name']} ({r['waste_category']})" for r in reports]
                chosen_r_str = st.selectbox("Select Incident Ticket", r_opts)
                chosen_uid = chosen_r_str.split(" - ")[0]
                target_r = next(r for r in reports if r["report_uid"] == chosen_uid)

                inc_pdf_path = generate_incident_pdf_report(target_r, f"nirmaan_incident_{chosen_uid}.pdf")
                with open(inc_pdf_path, "rb") as f:
                    inc_bytes = f.read()

                st.download_button(
                    label=f"Download Investigation PDF for {chosen_uid}",
                    data=inc_bytes,
                    file_name=f"nirmaan_{chosen_uid}_dossier.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )

    with tab_csv:
        st.markdown(
            """
            <div class="neu-card">
                <h3 style="margin-top: 0; color: #0F172A; font-size: 1.15rem;">
                    Filter & Export Tabular CSV Datasets
                </h3>
                <p style="font-size: 0.85rem; color: #64748B;">
                    Export full or filtered incident records including GPS coordinates, YOLO object counts,
                    OpenCV coverage, and priority scores.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            csv_ward = st.selectbox("Filter CSV Ward", ["All"] + wards)
        with fc2:
            csv_status = st.selectbox("Filter CSV Status", ["All", "Pending", "Under Cleanup", "Cleared", "Reopened"])
        with fc3:
            csv_cat = st.selectbox("Filter CSV Category", ["All", "mixed_trash", "plastic", "organic", "hazardous", "paper"])

        filtered_csv_reps = reports
        if csv_ward != "All":
            filtered_csv_reps = [r for r in filtered_csv_reps if r["ward_name"] == csv_ward]
        if csv_status != "All":
            filtered_csv_reps = [r for r in filtered_csv_reps if r["status"] == csv_status]
        if csv_cat != "All":
            filtered_csv_reps = [r for r in filtered_csv_reps if r["waste_category"] == csv_cat]

        st.caption(f"Filtered Records Matching Criteria: **{len(filtered_csv_reps)} records**")

        if filtered_csv_reps:
            csv_path = export_reports_to_csv(filtered_csv_reps, "nirmaan_filtered_reports.csv")
            with open(csv_path, "rb") as f:
                c_bytes = f.read()

            st.download_button(
                label=f"Download Filtered CSV ({len(filtered_csv_reps)} Rows)",
                data=c_bytes,
                file_name="nirmaan_bengaluru_reports_filtered.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )
        else:
            st.info("No records match the selected filter combination.")
