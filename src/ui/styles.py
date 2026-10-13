"""
NIRMAAN AI - Indian Government Civic-Tech Design System
Professional civic portal styling: Indian Naval Navy (#070F26), Crisp White (#FFFFFF),
Subtle Saffron (#D97706), and Emerald (#059669) accents.
Ensures 100% text contrast across all labels, inputs, tables, tabs, and expanders.
"""

from pathlib import Path
import re
import streamlit as st
from src.config import STYLES_DIR

CUSTOM_CSS_PATH = STYLES_DIR / "custom.css"


def apply_theme():
    """
    Injects custom government civic-portal CSS tokens safely via st.html(),
    guaranteeing crisp readability, no dark-on-dark text, and no raw CSS leaking.
    """
    custom_css = ""
    if CUSTOM_CSS_PATH.exists():
        try:
            with open(CUSTOM_CSS_PATH, "r", encoding="utf-8") as f:
                custom_css = f.read()
        except Exception:
            pass

    base_css = """
/* ==========================================================================
   Typography & Government Civic CSS Tokens
   ========================================================================== */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&display=swap');

:root {
    /* Surfaces */
    --bg-page-gradient: linear-gradient(180deg, #070F26 0%, #0B1736 100%);
    --bg-card-light: #FFFFFF;
    --bg-card-subtle: #F8FAFC;
    --bg-card-muted: #F1F5F9;

    /* Text on Dark Background */
    --text-on-dark-title: #FFFFFF;
    --text-on-dark-heading: #F8FAFC;
    --text-on-dark-body: #E2E8F0;
    --text-on-dark-muted: #94A3B8;

    /* Text on Light Surfaces */
    --text-on-light-title: #0F172A;
    --text-on-light-body: #1E293B;
    --text-on-light-secondary: #475569;
    --text-on-light-muted: #64748B;

    /* Borders */
    --border-light: #CBD5E1;
    --border-subtle: #E2E8F0;
    --border-dark: rgba(255, 255, 255, 0.16);
    --focus-ring: #2563EB;

    /* Civic Buttons */
    --btn-primary-gradient: linear-gradient(135deg, #059669 0%, #0D9488 100%);
    --btn-primary-hover: linear-gradient(135deg, #047857 0%, #0F766E 100%);
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* App Background: Deep Government Navy */
.stApp {
    background: linear-gradient(180deg, #070F26 0%, #0B1736 100%) !important;
    color: #F8FAFC;
}

.main, .block-container {
    background: transparent !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

/* Page Headings (Global Dark Background) */
.stApp h1, .stApp h2, .stApp h3 {
    color: #FFFFFF !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
}

.stApp h4, .stApp h5, .stApp h6 {
    color: #F1F5F9 !important;
    font-weight: 700 !important;
}

.stApp caption, .stCaption {
    color: #94A3B8 !important;
}

/* Paragraphs directly on dark background */
.stApp > div > p,
.block-container > div > p {
    color: #E2E8F0;
}

/* Widget Labels directly on Dark Background */
label[data-testid="stWidgetLabel"] p,
label[data-testid="stWidgetLabel"] span {
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}

/* Widget Labels inside Light Surfaces/Expanders/Cards */
div[data-testid="stExpander"] label[data-testid="stWidgetLabel"] p,
div[data-testid="stExpander"] label[data-testid="stWidgetLabel"] span,
.neu-card label[data-testid="stWidgetLabel"] p,
.neu-card label[data-testid="stWidgetLabel"] span,
.clean-table-card label[data-testid="stWidgetLabel"] p,
.clean-table-card label[data-testid="stWidgetLabel"] span {
    color: #0F172A !important;
}

/* ==========================================================================
   Form Inputs & Select Boxes
   ========================================================================== */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    border: 1px solid #CBD5E1 !important;
}

div[data-baseweb="input"] input:focus,
div[data-baseweb="textarea"] textarea:focus {
    border-color: #059669 !important;
    box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.25) !important;
}

div[data-baseweb="input"] input::placeholder,
div[data-baseweb="textarea"] textarea::placeholder {
    color: #64748B !important;
}

div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}

div[data-baseweb="select"] span {
    color: #0F172A !important;
    font-weight: 600 !important;
}

div[data-baseweb="popover"] ul,
div[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.15) !important;
}

div[data-baseweb="menu"] li,
div[data-baseweb="menu"] li span {
    color: #0F172A !important;
}

div[data-baseweb="menu"] li:hover {
    background-color: #F1F5F9 !important;
}

/* ==========================================================================
   Government Civic Metric Cards
   ========================================================================== */
div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border-radius: 12px !important;
    padding: 0.85rem 1.15rem !important;
    border: 1px solid #CBD5E1 !important;
    border-left: 4px solid #D97706 !important;
    box-shadow: 0 4px 16px rgba(5, 11, 26, 0.15) !important;
}

div[data-testid="stMetricLabel"] p,
div[data-testid="stMetricLabel"] span {
    color: #475569 !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

div[data-testid="stMetricValue"] div {
    color: #0F172A !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.85rem !important;
    font-weight: 800 !important;
}

.metric-card {
    background: #FFFFFF !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    border-left: 4px solid #059669 !important;
    box-shadow: 0 4px 16px rgba(5, 11, 26, 0.15) !important;
    border: 1px solid #CBD5E1 !important;
    color: #0F172A !important;
}

.metric-val {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #0F172A !important;
    line-height: 1.1 !important;
}

.metric-lbl {
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #475569 !important;
    margin-top: 0.35rem !important;
}

/* ==========================================================================
   Government Civic Cards (Light High-Contrast Surface)
   ========================================================================== */
.neu-card {
    background: #FFFFFF !important;
    border-radius: 14px !important;
    padding: 1.35rem 1.6rem !important;
    margin-bottom: 1.15rem !important;
    box-shadow: 0 6px 20px rgba(5, 11, 26, 0.16) !important;
    border: 1px solid #CBD5E1 !important;
    color: #1E293B !important;
}

.neu-card:hover {
    box-shadow: 0 10px 28px rgba(5, 11, 26, 0.22) !important;
}

.neu-card h1, .neu-card h2, .neu-card h3, .neu-card h4, .neu-card h5 {
    color: #0F172A !important;
    font-weight: 800 !important;
    text-shadow: none !important;
}

.neu-card p, .neu-card span, .neu-card div {
    color: #1E293B;
}

.neu-card strong, .neu-card b {
    color: #0F172A !important;
    font-weight: 700 !important;
}

/* ==========================================================================
   Clean Table Card & Civic Table
   ========================================================================== */
.clean-table-card {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    padding: 1.15rem !important;
    box-shadow: 0 6px 20px rgba(5, 11, 26, 0.16) !important;
    overflow-x: auto !important;
    margin-bottom: 1.5rem !important;
    color: #0F172A !important;
}

.civic-table {
    width: 100% !important;
    border-collapse: collapse !important;
    font-size: 0.88rem !important;
    background: #FFFFFF !important;
}

.civic-table th {
    background-color: #F8FAFC !important;
    color: #0F172A !important;
    font-weight: 800 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    border-bottom: 2px solid #CBD5E1 !important;
    padding: 0.85rem 1rem !important;
    text-align: left !important;
}

.civic-table td {
    padding: 0.85rem 1rem !important;
    border-bottom: 1px solid #E2E8F0 !important;
    color: #0F172A !important;
    vertical-align: middle !important;
    font-size: 0.88rem !important;
    background: #FFFFFF !important;
}

.civic-table td strong {
    color: #0F172A !important;
    font-weight: 700 !important;
}

.civic-table tr:hover td {
    background-color: #F1F5F9 !important;
}

/* ==========================================================================
   High-Contrast Status & Severity Badges
   ========================================================================== */
.badge {
    display: inline-block !important;
    padding: 0.28rem 0.65rem !important;
    border-radius: 9999px !important;
    font-size: 0.74rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
}

/* Severity Badges */
.badge-high {
    background-color: #FEE2E2 !important;
    color: #991B1B !important;
    border: 1px solid #F87171 !important;
}

.badge-med {
    background-color: #FEF3C7 !important;
    color: #92400E !important;
    border: 1px solid #FBBF24 !important;
}

.badge-low {
    background-color: #E0F2FE !important;
    color: #075985 !important;
    border: 1px solid #7DD3FC !important;
}

/* Operational Status Badges */
.badge-cleared {
    background-color: #DCFCE7 !important;
    color: #166534 !important;
    border: 1px solid #86EFAC !important;
}

.badge-progress {
    background-color: #FEF3C7 !important;
    color: #92400E !important;
    border: 1px solid #FBBF24 !important;
}

.badge-verify {
    background-color: #EDE9FE !important;
    color: #5B21B6 !important;
    border: 1px solid #C4B5FD !important;
}

.badge-assigned {
    background-color: #E0F2FE !important;
    color: #0369A1 !important;
    border: 1px solid #7DD3FC !important;
}

.badge-blocked {
    background-color: #FEE2E2 !important;
    color: #991B1B !important;
    border: 1px solid #F87171 !important;
}

.badge-reopened {
    background-color: #FFEDD5 !important;
    color: #9A3412 !important;
    border: 1px solid #FDBA74 !important;
}

.badge-pending {
    background-color: #F1F5F9 !important;
    color: #334155 !important;
    border: 1px solid #CBD5E1 !important;
}

/* Priority Score Pill */
.prio-pill {
    font-size: 0.95rem !important;
    font-weight: 800 !important;
    color: #0F172A !important;
    background-color: #F1F5F9 !important;
    border: 1px solid #94A3B8 !important;
    padding: 0.22rem 0.65rem !important;
    border-radius: 8px !important;
    display: inline-block !important;
    white-space: nowrap !important;
}

/* Civic Notice */
.civic-notice {
    background-color: #EFF6FF !important;
    border: 1px solid #BFDBFE !important;
    border-left: 4px solid #2563EB !important;
    padding: 0.85rem 1.15rem !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    color: #1E3A8A !important;
    margin-bottom: 1.25rem !important;
}

.civic-notice * {
    color: #1E3A8A !important;
}

/* ==========================================================================
   Primary & Secondary Action Buttons
   ========================================================================== */
/* Primary Buttons (Emerald/Teal Gradient with White Text) */
button[kind="primary"],
button[data-testid="baseButton-primary"],
div[data-testid="stFormSubmitButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #059669 0%, #0D9488 100%) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 14px rgba(5, 150, 105, 0.35) !important;
    transition: all 0.2s ease !important;
}

button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(135deg, #047857 0%, #0F766E 100%) !important;
    box-shadow: 0 6px 18px rgba(5, 150, 105, 0.5) !important;
    transform: translateY(-1px);
}

button[kind="primary"]:focus,
button[kind="primary"]:focus-visible {
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.4) !important;
    outline: none !important;
}

button[kind="primary"] p,
button[kind="primary"] span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* Secondary Buttons: Crisp White Surface with Dark Navy Text */
button[kind="secondary"],
button[data-testid="baseButton-secondary"],
div[data-testid="stFormSubmitButton"] button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
    transition: all 0.2s ease !important;
}

button[kind="secondary"]:hover,
button[data-testid="baseButton-secondary"]:hover {
    background: #F1F5F9 !important;
    color: #000000 !important;
    border-color: #94A3B8 !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12) !important;
    transform: translateY(-1px);
}

button[kind="secondary"]:focus,
button[kind="secondary"]:focus-visible,
button[kind="secondary"]:active {
    outline: 2px solid #2563EB !important;
    outline-offset: 1px !important;
    background: #E2E8F0 !important;
    color: #000000 !important;
}

button[kind="secondary"] p,
button[kind="secondary"] span {
    color: #0F172A !important;
    font-weight: 700 !important;
}

button[kind="secondary"]:hover p,
button[kind="secondary"]:hover span {
    color: #000000 !important;
}

/* Link Button (e.g. Navigate GPS Directions): White button with crisp dark text */
div[data-testid="stLinkButton"] a {
    background: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
    transition: all 0.2s ease !important;
    text-decoration: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

div[data-testid="stLinkButton"] a:hover {
    background: #F1F5F9 !important;
    color: #000000 !important;
    border-color: #94A3B8 !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12) !important;
    transform: translateY(-1px);
}

div[data-testid="stLinkButton"] a:focus,
div[data-testid="stLinkButton"] a:focus-visible,
div[data-testid="stLinkButton"] a:active {
    outline: 2px solid #2563EB !important;
    outline-offset: 1px !important;
    background: #E2E8F0 !important;
    color: #000000 !important;
}

div[data-testid="stLinkButton"] a p,
div[data-testid="stLinkButton"] a span {
    color: #0F172A !important;
    font-weight: 700 !important;
}

div[data-testid="stLinkButton"] a:hover p,
div[data-testid="stLinkButton"] a:hover span {
    color: #000000 !important;
}

/* ==========================================================================
   Expanders & Dropdowns
   ========================================================================== */
div[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    color: #0F172A !important;
    margin-bottom: 0.85rem !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06) !important;
    overflow: hidden !important;
}

div[data-testid="stExpander"] summary {
    background: #FFFFFF !important;
    color: #0F172A !important;
    padding: 0.85rem 1.15rem !important;
    border-radius: 10px !important;
    outline: none !important;
    cursor: pointer !important;
    transition: background 0.15s ease !important;
    user-select: none !important;
}

div[data-testid="stExpander"] summary:hover {
    background: #F8FAFC !important;
}

div[data-testid="stExpander"] summary:focus,
div[data-testid="stExpander"] summary:focus-visible {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.25) !important;
}

div[data-testid="stExpander"] summary p,
div[data-testid="stExpander"] summary span,
div[data-testid="stExpander"] summary div {
    color: #0F172A !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
}

div[data-testid="stExpander"] summary svg {
    fill: #0F172A !important;
    stroke: #0F172A !important;
}

div[data-testid="stExpander"] div[data-testid="stExpanderDetails"],
div[data-testid="stExpander"] div[data-testid="stVerticalBlock"] {
    background: #FFFFFF !important;
}

div[data-testid="stExpander"] p,
div[data-testid="stExpander"] span,
div[data-testid="stExpander"] div {
    color: #1E293B;
}

div[data-testid="stExpander"] .stCaption,
div[data-testid="stExpander"] caption {
    color: #475569 !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
}

/* File Uploader */
div[data-testid="stFileUploaderDropzone"] {
    background-color: #F8FAFC !important;
    border: 2px dashed #94A3B8 !important;
    border-radius: 8px !important;
}

div[data-testid="stFileUploaderDropzone"] span,
div[data-testid="stFileUploaderDropzone"] div,
div[data-testid="stFileUploaderDropzone"] small {
    color: #334155 !important;
}

div[data-testid="stFileUploaderDropzone"] button {
    background: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    font-weight: 700 !important;
}

div[data-testid="stFileUploaderDropzone"] button:hover {
    background: #E2E8F0 !important;
    color: #000000 !important;
}

/* ==========================================================================
   Tabs & Navigation Elements
   ========================================================================== */
button[data-baseweb="tab"] {
    color: #CBD5E1 !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
}

button[data-baseweb="tab"]:hover {
    color: #FFFFFF !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    font-weight: 800 !important;
    border-bottom-color: #D97706 !important;
    border-bottom-width: 3px !important;
}

/* Streamlit DataFrames & Tables */
div[data-testid="stDataFrame"] {
    background: #FFFFFF !important;
    border-radius: 8px !important;
    border: 1px solid #CBD5E1 !important;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
}

div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span {
    color: inherit !important;
    font-weight: 600 !important;
}

/* Top Navbar Container Isolation */
div[data-testid="stVerticalBlockBorderWrapper"]:has(#top-navbar-wrapper) {
    background: rgba(8, 17, 39, 0.95) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.16) !important;
    border-radius: 12px !important;
    padding: 0.5rem 1.25rem !important;
    margin-bottom: 1.25rem !important;
    box-shadow: 0 10px 25px rgba(5, 11, 26, 0.35) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(#top-navbar-wrapper) button {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #CBD5E1 !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 0.75rem !important;
    min-height: 36px !important;
    height: 36px !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
    white-space: nowrap !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(#top-navbar-wrapper) button:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    color: #FFFFFF !important;
    border-color: rgba(255, 255, 255, 0.15) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(#top-navbar-wrapper) button[kind="primary"] {
    background: rgba(5, 150, 105, 0.25) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(16, 185, 129, 0.6) !important;
    font-weight: 700 !important;
}

/* Civic Assistant Panel */
div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) {
    background: rgba(255, 255, 255, 0.98) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.90) !important;
    border-radius: 18px !important;
    padding: 1.25rem 1.25rem 1.1rem 1.25rem !important;
    box-shadow: 0 20px 45px rgba(5, 11, 26, 0.38) !important;
    color: #0F172A !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) p,
div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) span,
div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) label,
div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) div {
    color: #0F172A !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) button {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    color: #1E293B !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    padding: 0.35rem 0.65rem !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    transition: all 0.2s ease !important;
    min-height: 32px !important;
    height: 32px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) button:hover {
    background: #F1F5F9 !important;
    border-color: #94A3B8 !important;
    color: #0F172A !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) button[kind="primary"] {
    background: #059669 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 700 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) input {
    background: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}

/* Civic Assistant Streamlit Chat Messages */
div[data-testid="stChatMessage"] {
    background-color: #F8FAFC !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    padding: 0.65rem 0.85rem !important;
    margin-bottom: 0.65rem !important;
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.05) !important;
}

div[data-testid="stChatMessageContent"] {
    color: #0F172A !important;
}

div[data-testid="stChatMessageContent"] p,
div[data-testid="stChatMessageContent"] span,
div[data-testid="stChatMessageContent"] div {
    color: #0F172A !important;
    font-size: 0.88rem !important;
    line-height: 1.55 !important;
}

div[data-testid="stChatMessageContent"] strong,
div[data-testid="stChatMessageContent"] b {
    color: #0F172A !important;
    font-weight: 700 !important;
}

div[data-testid="stChatMessageContent"] ul,
div[data-testid="stChatMessageContent"] ol {
    margin: 0.4rem 0 !important;
    padding-left: 1.35rem !important;
    color: #0F172A !important;
}

div[data-testid="stChatMessageContent"] li {
    margin-bottom: 0.35rem !important;
    color: #1E293B !important;
    font-size: 0.86rem !important;
    line-height: 1.5 !important;
}

div[data-testid="stChatMessageContent"] li strong {
    color: #0F172A !important;
    font-weight: 700 !important;
}

div[data-testid="stChatMessageContent"] code {
    background-color: #E2E8F0 !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 4px !important;
    padding: 0.12rem 0.38rem !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
}

div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #0D9488 0%, #059669 100%) !important;
    border: none !important;
    box-shadow: 0 3px 10px rgba(5, 150, 105, 0.25) !important;
}

div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"],
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"] p,
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"] span {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

div[data-testid="stChatMessage"] [data-testid="stLatex"],
div[data-testid="stLatex"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    padding: 0.55rem 0.85rem !important;
    margin: 0.5rem 0 !important;
    overflow-x: auto !important;
    text-align: center !important;
}

div[data-testid="stChatMessage"] .katex,
div[data-testid="stChatMessage"] .katex-display,
div[data-testid="stChatMessage"] .katex-html,
div[data-testid="stLatex"] .katex,
div[data-testid="stLatex"] .katex-html,
.katex,
.katex * {
    color: #0F172A !important;
}
"""

    combined_css = f"{custom_css}\n{base_css}"
    clean_css = re.sub(r'\n{2,}', '\n', combined_css).strip()

    if hasattr(st, "html"):
        st.html(f"<style>\n{clean_css}\n</style>")
    else:
        st.markdown(f"<style>\n{clean_css}\n</style>", unsafe_allow_html=True)
