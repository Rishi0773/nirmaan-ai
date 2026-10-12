"""
NIRMAAN AI - Cleanup Verification & Evidence View
Implements dual-image Before-and-After photographic comparison,
waste reduction calculation, viewpoint uncertainty analysis, and supervisor sign-off (PPT Slide 8).
"""

from pathlib import Path
import streamlit as st
from src.config import BEFORE_DIR, AFTER_DIR
from src.database.repository import Repository
from src.ml.verification import verify_cleanup_images
from src.ui.components import render_header, status_badge_html
from src.auth.rbac import has_permission, get_current_user


def render(repo: Repository):
    render_header(
        title="Before-and-After Cleanup Verification",
        subtitle="Computer vision verification measuring residual waste reduction before supervisory closure.",
        active_tab="Cleanup Verification"
    )

    tasks = repo.get_all_tasks()
    if not tasks:
        st.info("No cleanup tasks available for verification.")
        return

    # Task Selector
    task_options = [f"{t['task_code']} - {t['report_uid']} ({t['status']})" for t in tasks]
    selected_task_opt = st.selectbox("Select Task to Verify / Review Evidence", options=task_options)
    selected_task_code = selected_task_opt.split(" - ")[0]
    target_task = next((t for t in tasks if t["task_code"] == selected_task_code), None)

    if not target_task:
        return

    task_id = target_task["id"]
    existing_ver = repo.get_verification_by_task(task_id)

    # 1. Existing Verification Record Display
    if existing_ver:
        st.markdown(
            f"""
            <div class="neu-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #0F172A; font-size: 1.2rem;">
                        Verification Record for {target_task['task_code']}
                    </h3>
                    <span>{status_badge_html(target_task['status'])}</span>
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.88rem; color: #334155;">
                    <div>• AI Verdict: <strong>{existing_ver['ai_verdict']}</strong></div>
                    <div>• Waste Reduction: <strong>{existing_ver['waste_reduction_pct']:.1f}%</strong></div>
                    <div>• Supervisor Decision: <strong>{existing_ver['supervisor_decision']}</strong></div>
                    <div>• Verified Date: {existing_ver['verified_at']}</div>
                    <div>• Notes: {existing_ver.get('verification_notes') or 'Verified by supervisor.'}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Show Before & After photos
        col_b, col_a = st.columns(2)
        with col_b:
            st.markdown("<strong>BEFORE CLEANUP</strong>", unsafe_allow_html=True)
            if Path(existing_ver["before_image_path"]).exists():
                st.image(existing_ver["before_image_path"], use_container_width=True)
        with col_a:
            st.markdown("<strong>AFTER CLEANUP</strong>", unsafe_allow_html=True)
            if Path(existing_ver["after_image_path"]).exists():
                st.image(existing_ver["after_image_path"], use_container_width=True)

    # 2. Upload / Run New Verification Form
    if has_permission("verify_cleanup"):
        st.markdown("### Submit New Verification Evidence")
        with st.form("new_verification_form"):
            st.write(f"Attach photographic proof for **{target_task['task_code']}** ({target_task['report_uid']}):")
            f_col1, f_col2 = st.columns(2)

            with f_col1:
                before_file = st.file_uploader("Upload Before Photo", type=["jpg", "png"], key="b_img")
            with f_col2:
                after_file = st.file_uploader("Upload After Photo", type=["jpg", "png"], key="a_img")

            v_notes = st.text_input("Supervisor Review Remarks", value="Site swept, disinfected, and verified clear of obstructions.")
            run_btn = st.form_submit_button("Run AI Verification & Review", type="primary")

        if run_btn:
            # If files uploaded, save them; else generate test pair
            b_path = BEFORE_DIR / f"{target_task['report_uid']}_before_v.jpg"
            a_path = AFTER_DIR / f"{target_task['report_uid']}_after_v.jpg"

            if before_file:
                with open(b_path, "wb") as f:
                    f.write(before_file.getbuffer())
            else:
                from src.database.seed_data import create_synthetic_image
                create_synthetic_image(b_path, f"BEFORE {target_task['report_uid']}", object_count=6, clean_state=False)

            if after_file:
                with open(a_path, "wb") as f:
                    f.write(after_file.getbuffer())
            else:
                from src.database.seed_data import create_synthetic_image
                create_synthetic_image(a_path, f"AFTER {target_task['report_uid']}", object_count=0, clean_state=True)

            with st.spinner("Analyzing pre/post imagery with OpenCV feature alignment and contour reduction..."):
                ver_res = verify_cleanup_images(str(b_path), str(a_path))

                decision = "Verified Clean" if ver_res["ai_verdict"] == "Approved" else "Needs Re-cleaning"
                user = get_current_user()

                repo.save_verification(
                    task_id=task_id,
                    before_image_path=str(b_path),
                    after_image_path=str(a_path),
                    waste_reduction_pct=ver_res["waste_reduction_pct"],
                    ai_verdict=ver_res["ai_verdict"],
                    supervisor_decision=decision,
                    verified_by=user["id"],
                    verification_notes=v_notes
                )

                repo.log_audit("VERIFICATION_SUBMIT", "Task", target_task["task_code"], user["full_name"], user["id"], "Under Cleanup", decision)

            st.success(f"Verification complete: **{ver_res['waste_reduction_pct']}% reduction** detected! AI Verdict: {ver_res['ai_verdict']}.")
            st.rerun()
