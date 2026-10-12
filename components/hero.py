"""
NIRMAAN AI - Full-Width Dominant Hero Section Component
Integrates the assets/images/bengaluru_hero.jpg photograph as the dominant backdrop
across the main viewport with a dark translucent navy gradient overlay and reference layout.
"""

import base64
import logging
from pathlib import Path
import streamlit as st
from src.config import HERO_IMAGE_PATH, BASE_DIR
from src.database.repository import Repository
from services.search_service import search_reports
from components.civic_assistant import render_civic_assistant


def get_hero_image_b64() -> tuple[str, str]:
    """
    Resolves the hero image relative to project root,
    reads binary data, and returns (mime_type, base64_string).
    If missing, returns ("", "").
    """
    candidates = [
        HERO_IMAGE_PATH,                              # assets/images/bengaluru_hero.jpg
        HERO_IMAGE_PATH.with_suffix(".png"),          # assets/images/bengaluru_hero.png
        HERO_IMAGE_PATH.with_suffix(".jpeg"),
        BASE_DIR / "assets" / "images" / "bengaluru_hero.jpg"
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            try:
                mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
                with open(p, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                return mime, b64
            except Exception as e:
                logging.warning(f"Failed to read hero image from {p}: {e}")

    logging.warning("Hero background image not found in assets/images/. Using fallback gradient.")
    return "", ""


def get_hero_background_style() -> str:
    """Returns CSS background property with image or dark navy gradient fallback."""
    mime, b64 = get_hero_image_b64()
    if b64:
        return (
            f"background: linear-gradient(135deg, rgba(8, 17, 39, 0.80) 0%, rgba(13, 27, 62, 0.70) 50%, rgba(8, 17, 39, 0.84) 100%), "
            f"url('data:{mime};base64,{b64}') center center / cover no-repeat fixed;"
        )
    return "background: linear-gradient(135deg, #0A1128 0%, #0D1B3E 45%, #0F3854 85%, #052E2B 100%);"


import textwrap


def render_hero(repo: Repository):
    """Renders the full-width dominant hero section matching the approved reference design."""
    mime, b64 = get_hero_image_b64()

    if b64:
        bg_css = f"""
.stApp, div[data-testid="stAppViewContainer"] {{
    background: linear-gradient(135deg, rgba(8, 17, 39, 0.78) 0%, rgba(13, 27, 62, 0.68) 50%, rgba(8, 17, 39, 0.82) 100%),
                url('data:{mime};base64,{b64}') center center / cover no-repeat fixed !important;
    background-size: cover !important;
    background-position: center center !important;
    background-attachment: fixed !important;
}}
"""
    else:
        bg_css = """
.stApp, div[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0A1128 0%, #0D1B3E 45%, #0F3854 85%, #052E2B 100%) fixed !important;
}
"""

    st.markdown(
        textwrap.dedent(f"""<style>
{bg_css}

/* Ensure Streamlit wrappers are transparent to reveal the background photo */
.main, .block-container, div[data-testid="stVerticalBlock"] {{
    background: transparent !important;
}}
header[data-testid="stHeader"] {{
    background: transparent !important;
}}

/* Hero Universal Search Form Glass Styling */
div[data-testid="stForm"]:has(input[aria-label="HeroSearch"]) {{
    background: rgba(255, 255, 255, 0.12) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.28) !important;
    border-radius: 12px !important;
    padding: 0.4rem 0.65rem !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
    margin-bottom: 1.25rem !important;
}}
div[data-testid="stForm"]:has(input[aria-label="HeroSearch"]) input {{
    background: transparent !important;
    color: #FFFFFF !important;
    border: none !important;
    font-size: 0.92rem !important;
    padding-left: 0.5rem !important;
}}
div[data-testid="stForm"]:has(input[aria-label="HeroSearch"]) input::placeholder {{
    color: rgba(226, 232, 240, 0.75) !important;
}}
div[data-testid="stForm"]:has(input[aria-label="HeroSearch"]) button {{
    background: rgba(255, 255, 255, 0.18) !important;
    border: 1px solid rgba(255, 255, 255, 0.35) !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.2s ease !important;
}}
div[data-testid="stForm"]:has(input[aria-label="HeroSearch"]) button:hover {{
    background: rgba(255, 255, 255, 0.28) !important;
    border-color: rgba(255, 255, 255, 0.6) !important;
}}

/* Hero Primary & Secondary CTA Buttons */
button[key="hero_btn_report"] {{
    background: #2563EB !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.25rem !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 18px rgba(37, 99, 235, 0.45) !important;
    transition: all 0.2s ease !important;
}}
button[key="hero_btn_report"]:hover {{
    background: #1D4ED8 !important;
    box-shadow: 0 6px 24px rgba(37, 99, 235, 0.6) !important;
    transform: translateY(-2px);
}}

button[key="hero_btn_map"] {{
    background: rgba(255, 255, 255, 0.12) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.32) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.25rem !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
}}
button[key="hero_btn_map"]:hover {{
    background: rgba(255, 255, 255, 0.22) !important;
    border-color: rgba(255, 255, 255, 0.55) !important;
    transform: translateY(-2px);
}}
</style>"""),
        unsafe_allow_html=True
    )

    # Hero Content Grid (Left Content + Right Civic Assistant)
    col_left, col_right = st.columns([1.35, 1.0], gap="large")

    with col_left:
        # Eyebrow text
        st.markdown(
            """
            <div style="font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em; color: #2DD4BF; margin-bottom: 0.85rem;">
                CLEANER STREETS · HEALTHIER COMMUNITIES · A BETTER BENGALURU
            </div>
            <div style="font-family: 'Space Grotesk', 'Plus Jakarta Sans', sans-serif; font-size: clamp(2.4rem, 4.4vw, 3.8rem); font-weight: 800; color: #FFFFFF; line-height: 1.12; letter-spacing: -0.03em; margin-bottom: 0.95rem; text-shadow: 0 2px 10px rgba(0,0,0,0.5);">
                A Cleaner Bengaluru<br/>
                <span style="color: #10B981;">Starts Here.</span>
            </div>
            <div style="font-size: 1.05rem; line-height: 1.6; color: #E2E8F0; max-width: 580px; margin-bottom: 1.6rem; text-shadow: 0 1px 4px rgba(0,0,0,0.5);">
                Report waste hotspots, track cleanup progress, and help sanitation teams prioritize locations that need attention.
            </div>
            """,
            unsafe_allow_html=True
        )

        # Translucent Universal Search Bar
        with st.form("hero_search_form"):
            s_col1, s_col2 = st.columns([3.4, 1])
            with s_col1:
                search_q = st.text_input(
                    "HeroSearch",
                    placeholder="Search by report ID, ward, or locality...",
                    label_visibility="collapsed"
                )
            with s_col2:
                searched = st.form_submit_button("Search", use_container_width=True)

        if searched and search_q.strip():
            matches = search_reports(search_q.strip(), repo)
            if matches:
                st.success(f"Found {len(matches)} matching report(s):")
                for m in matches[:3]:
                    mc1, mc2 = st.columns([3, 1])
                    with mc1:
                        st.markdown(
                            f"<div style='color:#FFFFFF; font-size:0.86rem;'><strong>{m['report_uid']}</strong> — {m['ward_name']} | <em>{m['status']}</em> ({m['waste_category'].replace('_', ' ')})</div>",
                            unsafe_allow_html=True
                        )
                    with mc2:
                        if st.button("Inspect", key=f"insp_hero_{m['report_uid']}", use_container_width=True):
                            st.session_state["nav_page"] = "Track Report"
                            st.session_state["selected_report_uid"] = m["report_uid"]
                            st.rerun()
            else:
                st.warning(f"No records found matching '{search_q}'. Try 'Koramangala' or 'REP-BLR-001'.")

        st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)

        # Primary and Secondary CTA Buttons
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("Report a Garbage Hotspot", key="hero_btn_report", use_container_width=True):
                st.session_state["nav_page"] = "Report Garbage"
                st.rerun()
        with btn_c2:
            if st.button("Explore Live Hotspot Map", key="hero_btn_map", use_container_width=True):
                st.session_state["nav_page"] = "Live Map"
                st.rerun()

        # Civic Assurance Note
        st.markdown(
            """
            <div style="margin-top: 1.5rem; padding: 0.75rem 1rem; background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.16); border-radius: 10px; font-size: 0.8rem; color: #E2E8F0;">
                <strong style="color: #2DD4BF;">Civic Decision-Support Protocol:</strong> Reports are evaluated in real time via YOLOv8 multi-class detection and DBSCAN recurrence clustering to optimize municipal collection dispatches.
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_right:
        render_civic_assistant(repo)

