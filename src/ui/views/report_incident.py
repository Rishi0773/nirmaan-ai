"""
NIRMAAN AI - Incident Reporting View
Enables citizens and field workers to submit waste photographs,
validates geographic coordinates, triggers real-time YOLOv8/OpenCV analysis,
and commits records to SQLite storage (PPT Slide 3 & 4).
"""

import uuid
from datetime import datetime
from pathlib import Path
import streamlit as st
import numpy as np
import cv2

from src.config import (
    REPORTS_DIR, WASTE_CLASSES, BENGALURU_BOUNDS
)
from src.database.repository import Repository
from src.ml.detector import detect_waste
from src.ml.severity import compute_waste_coverage, evaluate_severity
from src.ml.clustering import run_hotspot_clustering
from src.engine.priority import calculate_and_save_all_priorities
from src.ui.components import render_header, severity_badge_html


def render(repo: Repository):
    render_header(
        title="Report Garbage Incident",
        subtitle="Capture waste photographs and location coordinates for automated computer vision triage.",
        active_tab="Report Incident"
    )

    st.markdown(
        """
        <div class="neu-card">
            <h4 style="margin-top: 0; color: #0F172A;">Incident Submission Form</h4>
            <p style="font-size: 0.85rem; color: #64748B;">
                Upload a clear photographic image of the street or open blackspot.
                Coordinates must fall within the municipal boundary.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("incident_report_form", clear_on_submit=False):
        col1, col2 = st.columns([1.2, 1])

        with col1:
            uploaded_file = st.file_uploader(
                "Upload Garbage Photo (JPG / PNG)",
                type=["jpg", "jpeg", "png"],
                help="High-contrast daytime photographs yield optimal YOLO detection accuracy."
            )

            # Quick Location Selector for Bengaluru Wards
            ward_preset = st.selectbox(
                "Select Bengaluru Ward Preset (or enter custom coordinates below)",
                options=[
                    "Koramangala (12.9352, 77.6245)",
                    "Indiranagar (12.9719, 77.6412)",
                    "Malleshwaram (13.0031, 77.5701)",
                    "Whitefield (12.9863, 77.7289)",
                    "Jayanagar (12.9299, 77.5834)",
                    "Shivajinagar (12.9830, 77.6050)",
                    "HSR Layout (12.9116, 77.6389)",
                    "Custom Coordinates"
                ]
            )

            # Coordinate Inputs
            coord_col1, coord_col2 = st.columns(2)
            default_lat = 12.9352
            default_lon = 77.6245
            if "Indiranagar" in ward_preset:
                default_lat, default_lon = 12.9719, 77.6412
            elif "Malleshwaram" in ward_preset:
                default_lat, default_lon = 13.0031, 77.5701
            elif "Whitefield" in ward_preset:
                default_lat, default_lon = 12.9863, 77.7289
            elif "Jayanagar" in ward_preset:
                default_lat, default_lon = 12.9299, 77.5834
            elif "Shivajinagar" in ward_preset:
                default_lat, default_lon = 12.9830, 77.6050
            elif "HSR Layout" in ward_preset:
                default_lat, default_lon = 12.9116, 77.6389

            with coord_col1:
                lat = st.number_input("Latitude", value=default_lat, format="%.5f")
            with coord_col2:
                lon = st.number_input("Longitude", value=default_lon, format="%.5f")

            address = st.text_input("Street Address / Landmark", value="5th Block near Bus Stop", max_chars=120)

        with col2:
            ward_name = ward_preset.split(" ")[0] if "Custom" not in ward_preset else "Bengaluru Central"
            ward_name_input = st.text_input("Ward Name", value=ward_name)

            waste_cat = st.selectbox(
                "Primary Waste Category (Citizen Observation)",
                options=WASTE_CLASSES,
                index=WASTE_CLASSES.index("mixed_trash")
            )

            description = st.text_area(
                "Incident Description",
                placeholder="Describe accumulation size, any drain blockages, offensive odors, or public hazard...",
                height=110
            )

            from src.auth.rbac import get_current_user
            current_user = get_current_user()
            default_rep_name = current_user.get("full_name", "Civic Citizen")
            reporter_name = st.text_input("Reporter Name", value=default_rep_name)

        submitted = st.form_submit_button("Submit Incident & Run AI Triage", use_container_width=True, type="primary")

    # Duplicate warning check for coordinates
    nearby_dups = repo.find_duplicate_reports(lat, lon, waste_category=waste_cat, max_meters=60.0)
    if nearby_dups:
        dup = nearby_dups[0]
        st.warning(
            f"⚠️ **Duplicate Warning:** An active complaint `{dup['report_uid']}` ({dup['status']}) was logged "
            f"**{dup['distance_meters']} meters away** at {dup.get('address')}. "
            "If this refers to the same site, you can append a follow-up note in **Track Report** to prevent duplicate work."
        )

    if submitted:
        # Validate coordinates against Bengaluru bounds
        if not (BENGALURU_BOUNDS["lat_min"] <= lat <= BENGALURU_BOUNDS["lat_max"] and
                BENGALURU_BOUNDS["lon_min"] <= lon <= BENGALURU_BOUNDS["lon_max"]):
            st.warning(f"Note: Coordinates ({lat:.4f}, {lon:.4f}) lie outside Greater Bengaluru standard bounds. Tagging with boundary notice.")

        # Generate unique ticket ID
        report_uid = f"REP-BLR-{uuid.uuid4().hex[:6].upper()}"

        # Save image file
        image_path = None
        if uploaded_file is not None:
            image_filename = f"{report_uid}_upload.jpg"
            image_path = REPORTS_DIR / image_filename
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        else:
            # Generate demonstration synthetic street waste image if user did not upload a file
            from src.database.seed_data import create_synthetic_image
            image_filename = f"{report_uid}_simulated.jpg"
            image_path = REPORTS_DIR / image_filename
            create_synthetic_image(image_path, address or "Bengaluru Street", object_count=5)

        with st.spinner("Analyzing waste photograph using YOLOv8 & OpenCV..."):
            # 1. Run Detection
            det_results = detect_waste(str(image_path), report_uid)

            # 2. Compute Coverage & Severity
            coverage_pct = compute_waste_coverage(str(image_path))
            sev_results = evaluate_severity(
                total_objects=det_results["total_objects"],
                coverage_ratio=coverage_pct,
                detected_classes=det_results["detected_classes"],
                waste_category=waste_cat
            )

            # 3. Save to Database
            from src.auth.rbac import get_current_user
            current_user = get_current_user()

            rep_id = repo.create_report(
                report_uid=report_uid,
                latitude=lat,
                longitude=lon,
                ward_name=ward_name_input,
                waste_category=waste_cat,
                address=address,
                description=description,
                reporter_name=reporter_name,
                is_simulated=0 if uploaded_file else 1,
                citizen_id=current_user.get("id")
            )

            repo.add_report_image(rep_id, "incident", str(image_path), det_results.get("annotated_path", ""))

            repo.save_detection(
                report_id=rep_id,
                model_version=det_results["model_version"],
                total_objects=det_results["total_objects"],
                detected_classes=det_results["detected_classes"],
                bounding_boxes=det_results["bounding_boxes"],
                max_confidence=det_results["max_confidence"],
                inference_time_ms=det_results["inference_time_ms"]
            )

            repo.save_severity(
                report_id=rep_id,
                severity_level=sev_results["severity_level"],
                severity_score=sev_results["severity_score"],
                coverage_ratio=sev_results["coverage_ratio"],
                factors=sev_results["factors"],
                assessed_by=det_results["model_version"]
            )

            # 4. Trigger Spatial Clustering & Priority Recalculation
            run_hotspot_clustering(repo)
            calculate_and_save_all_priorities(repo)

            # 5. Log Audit and Add Notification
            repo.log_audit("REPORT_CREATE", "Report", report_uid, reporter_name, None, "", f"Created {report_uid} with severity {sev_results['severity_level']}")
            repo.add_notification(
                title=f"New Report: {report_uid}",
                message=f"Reported at {address} ({ward_name_input}). Severity: {sev_results['severity_level']}.",
                category="Priority Alert" if sev_results["severity_level"] == "High" else "System",
                target_role="Sanitation Supervisor",
                link_ref=report_uid
            )

        st.success(f"Report **{report_uid}** successfully registered and prioritized!")

        # Display Live Inference Summary
        st.markdown("### AI Computer Vision Assessment Results")
        img_col1, img_col2 = st.columns(2)
        with img_col1:
            st.markdown("<strong>Original Uploaded Photograph</strong>", unsafe_allow_html=True)
            st.image(str(image_path), caption="Source Street View", use_container_width=True)
        with img_col2:
            st.markdown("<strong>AI Annotated Detections & Saliency Mask</strong>", unsafe_allow_html=True)
            annot_path = det_results.get("annotated_path", str(image_path))
            st.image(annot_path, caption=f"{det_results['model_version']} (Inference: {det_results['inference_time_ms']} ms)", use_container_width=True)

        if det_results["total_objects"] == 0:
            st.info("ℹ️ No discrete bounding boxes detected with confidence > 0.25. Evaluated via OpenCV surface saliency and ground coverage.")

        st.markdown(
            f"""
            <div class="neu-card">
                <div style="font-size: 0.82rem; color: #64748B; font-weight: 600;">ASSESSED SEVERITY</div>
                <div style="margin: 0.25rem 0 0.5rem 0;">{severity_badge_html(sev_results['severity_level'])}</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">
                    Severity Score: {sev_results['severity_score']}/100
                </div>
                <p style="font-size: 0.85rem; color: #334155; margin-top: 0.5rem;">
                    <strong>Rationale:</strong> {sev_results['factors']['grading_rationale']}
                </p>
                <hr style="border: 0; border-top: 1px solid #E2E8F0; margin: 0.75rem 0;"/>
                <div style="font-size: 0.82rem; color: #475569;">
                    <div>• Detected Objects: <strong>{det_results['total_objects']} items</strong> ({', '.join([f'{k}: {v}' for k,v in det_results['detected_classes'].items()]) if det_results['detected_classes'] else 'None'})</div>
                    <div>• Ground Coverage: <strong>{sev_results['coverage_ratio']}%</strong></div>
                    <div>• Max Confidence: <strong>{det_results['max_confidence']:.2f}</strong></div>
                    <div>• Model Backend: <strong>{det_results['model_type']}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
