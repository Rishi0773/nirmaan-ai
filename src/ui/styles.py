"""
NIRMAAN AI - Restrained Neumorphism Design System
CSS tokens, card structures, badges, and layout aesthetics
tailored for municipal decision-makers and academic defense.
"""

from pathlib import Path
import streamlit as st
from src.config import STYLES_DIR

CUSTOM_CSS_PATH = STYLES_DIR / "custom.css"


def apply_theme():
    """Injects custom restrained neumorphic & modern civic reference CSS tokens."""
    custom_css = ""
    if CUSTOM_CSS_PATH.exists():
        try:
            with open(CUSTOM_CSS_PATH, "r", encoding="utf-8") as f:
                custom_css = f.read()
        except Exception:
            pass

    if custom_css:
        st.markdown(f"<style>\n{custom_css}\n</style>", unsafe_allow_html=True)

    st.markdown(
        """
        <style>

        /* Base typography & backgrounds */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #1E293B;
        }

        /* App container background */
        .stApp {
            background-color: #F1F5F9;
        }

        /* Restrained Neumorphic Cards */
        .neu-card {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 4px 4px 10px rgba(160, 175, 195, 0.25),
                        -4px -4px 10px rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(226, 232, 240, 0.8);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        .neu-card:hover {
            box-shadow: 6px 6px 14px rgba(160, 175, 195, 0.35),
                        -5px -5px 12px rgba(255, 255, 255, 1.0);
        }

        /* Metric Cards */
        .metric-card {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            border-left: 4px solid #059669;
            box-shadow: 3px 3px 8px rgba(180, 190, 205, 0.25),
                        -3px -3px 8px rgba(255, 255, 255, 0.9);
        }

        .metric-val {
            font-size: 1.85rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.1;
        }

        .metric-lbl {
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748B;
            margin-top: 0.35rem;
        }

        /* Severity Badges */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.025em;
        }

        .badge-high {
            background-color: #FEE2E2;
            color: #DC2626;
            border: 1px solid #FCA5A5;
        }

        .badge-med {
            background-color: #FEF3C7;
            color: #D97706;
            border: 1px solid #FCD34D;
        }

        .badge-low {
            background-color: #E0F2FE;
            color: #0284C7;
            border: 1px solid #BAE6FD;
        }

        .badge-cleared {
            background-color: #DCFCE7;
            color: #16A34A;
            border: 1px solid #86EFAC;
        }

        .badge-pending {
            background-color: #F1F5F9;
            color: #475569;
            border: 1px solid #CBD5E1;
        }

        /* Priority Score pill */
        .prio-pill {
            font-size: 1.15rem;
            font-weight: 700;
            color: #0F172A;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            padding: 0.2rem 0.6rem;
            border-radius: 8px;
            display: inline-block;
        }

        /* Civic Disclaimer Banner */
        .civic-notice {
            background-color: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-left: 4px solid #2563EB;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-size: 0.82rem;
            color: #1E40AF;
            margin-bottom: 1.25rem;
        }

        /* Streamlit Input Styling */
        div[data-baseweb="select"] > div {
            border-radius: 8px !important;
            border-color: #CBD5E1 !important;
        }

        /* Buttons with soft neumorphic lift */
        button[kind="primary"] {
            background-color: #059669 !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            box-shadow: 2px 2px 6px rgba(5, 150, 105, 0.3) !important;
            transition: all 0.2s ease !important;
        }

        button[kind="primary"]:hover {
            background-color: #047857 !important;
            box-shadow: 3px 3px 10px rgba(5, 150, 105, 0.45) !important;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
            box-shadow: 2px 0 10px rgba(180, 190, 205, 0.15);
        }

        /* Hide Streamlit default header decoration */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
