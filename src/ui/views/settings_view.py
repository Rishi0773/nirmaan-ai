"""
NIRMAAN AI - Settings & Engine Calibration View
Allows tuning of mathematical priority weights, inspecting model weights,
and resetting or re-seeding the demonstration database.
"""

from pathlib import Path
import streamlit as st
from src.config import (
    DEFAULT_PRIORITY_WEIGHTS, CUSTOM_YOLO_WEIGHTS, DB_PATH
)
from src.database.repository import Repository
from src.database.seed_data import seed_database
from src.engine.priority import calculate_and_save_all_priorities
from src.ui.components import render_header
from src.auth.rbac import has_permission, get_current_user


def render(repo: Repository):
    if not has_permission("tune_weights"):
        st.error("Access Restricted: Mathematical calibration and system settings are restricted to Administrators.")
        st.info("Please switch to an Administrator profile via the Login / Role Switcher to access this console.")
        return

    render_header(
        title="Settings & Mathematical Calibration",
        subtitle="Calibrate priority scoring weights, inspect model weights, and manage database state.",
        active_tab="Settings"
    )

    # 1. Prioritization Weights Calibration
    st.markdown("### Mathematical Prioritization Formula Calibration")
    st.markdown(
        """
        <div class="neu-card">
            <p style="font-size: 0.85rem; color: #334155; margin: 0;">
                Formula: <code>Score = w_s · S + w_r · R + w_w · W + w_t · T</code><br/>
                Weights should sum to 1.00 (100%) for normalized municipal triage.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if "weights" not in st.session_state:
        st.session_state.weights = dict(DEFAULT_PRIORITY_WEIGHTS)

    with st.form("calibrate_weights_form"):
        w_col1, w_col2 = st.columns(2)
        with w_col1:
            ws = st.slider("Severity Weight (w_s)", 0.05, 0.60, float(st.session_state.weights["severity"]), 0.05)
            wr = st.slider("Recurrence Weight (w_r)", 0.05, 0.60, float(st.session_state.weights["recurrence"]), 0.05)
        with w_col2:
            ww = st.slider("Waste Hazard Weight (w_w)", 0.05, 0.60, float(st.session_state.weights["waste_type"]), 0.05)
            wt = st.slider("Waiting Time Urgency Weight (w_t)", 0.05, 0.60, float(st.session_state.weights["waiting_time"]), 0.05)

        total_w = ws + wr + ww + wt
        st.write(f"Total Normalized Sum: **{total_w:.2f}** " + ("(Balanced 1.00)" if abs(total_w - 1.0) < 0.01 else "(Will be normalized)"))

        btn_save = st.form_submit_button("Apply Weights & Recalculate Priority Queue", type="primary")

    if btn_save:
        norm = {
            "severity": ws / total_w,
            "recurrence": wr / total_w,
            "waste_type": ww / total_w,
            "waiting_time": wt / total_w
        }
        st.session_state.weights = norm
        calculate_and_save_all_priorities(repo, custom_weights=norm)
        user = get_current_user()
        repo.log_audit("WEIGHTS_UPDATE", "Engine", "FORMULA", user["full_name"], user["id"], str(DEFAULT_PRIORITY_WEIGHTS), str(norm))
        st.success("New priority weights calibrated and applied to all pending tickets!")
        st.rerun()

    st.markdown("---")

    # 2. Model Weights Status
    st.markdown("### Computer Vision Model Status")
    custom_exists = CUSTOM_YOLO_WEIGHTS.exists()

    st.markdown(
        f"""
        <div class="neu-card">
            <div style="font-size: 0.9rem; color: #0F172A; font-weight: 700;">
                Model Configuration
            </div>
            <div style="font-size: 0.84rem; color: #334155; margin-top: 0.5rem;">
                <div>• Custom Trained Weights Path: <code>{CUSTOM_YOLO_WEIGHTS}</code></div>
                <div>• Custom Weights Present: <strong>{'Yes (Fine-tuned)' if custom_exists else 'No (Using Pretrained YOLOv8 Base + OpenCV Saliency)'}</strong></div>
                <div>• Database Location: <code>{DB_PATH}</code></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. Database State Management (Reset / Re-seed)
    if has_permission("tune_weights"):
        st.markdown("### Development Database Reset & Re-seeding")
        st.markdown(
            """
            <p style="font-size: 0.85rem; color: #64748B;">
                Resets all tables and populates with realistic Bengaluru demonstration reports across Koramangala,
                Indiranagar, Malleshwaram, Whitefield, and Jayanagar.
            </p>
            """,
            unsafe_allow_html=True
        )

        if st.button("Reset & Re-seed Demonstration Database", type="primary"):
            with st.spinner("Re-seeding database and generating test images..."):
                seed_database()
                st.success("Database successfully reset and re-seeded with 15 Bengaluru demonstration reports.")
                st.rerun()
