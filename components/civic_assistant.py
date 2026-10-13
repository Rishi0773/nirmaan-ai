"""
NIRMAAN AI - Floating Civic Assistant Component
Interactive civic guidance, rule-based decision support,
and real SQLite report tracking with high-contrast readable styling.
Renders native Markdown and LaTeX math blocks inside st.chat_message.
"""

import re
import streamlit as st
from src.database.repository import Repository
from services.assistant_service import process_assistant_query


def render_assistant_content(content: str):
    """
    Renders assistant content splitting markdown text and standalone LaTeX equations.
    Guarantees that equations are rendered via st.latex() and text via st.markdown().
    Handles multiple equations, edge cases, and fallbacks cleanly.
    """
    if not content:
        return

    # Pattern to find $$...$$ blocks
    equation_pattern = re.compile(r'(\$\$[\s\S]*?\$\$)', re.MULTILINE)
    parts = equation_pattern.split(content)

    for part in parts:
        if not part:
            continue
        trimmed = part.strip()
        if trimmed.startswith("$$") and trimmed.endswith("$$") and len(trimmed) >= 4:
            # Extract raw formula without $$ delimiters
            raw_formula = trimmed[2:-2].strip()
            try:
                st.latex(raw_formula)
            except Exception:
                # Fallback to readable formatted markdown if latex rendering fails
                st.markdown(f"> **Formula:** `{raw_formula}`")
        else:
            # Surrounding explanation as native Streamlit Markdown
            st.markdown(part)


def render_civic_assistant(repo: Repository):
    """Renders the single, unified, light translucent civic assistant panel."""
    if "assistant_history" not in st.session_state:
        st.session_state["assistant_history"] = [
            {
                "sender": "assistant",
                "text": "Hello! I am your NIRMAAN Civic Assistant. I can help you report garbage blackspots, track complaints, or explain municipal priority scoring.",
                "action": None
            }
        ]

    # Verify real service health (do not fabricate online status)
    is_online = False
    try:
        _ = repo.get_dashboard_metrics()
        is_online = True
    except Exception:
        is_online = False

    status_dot = "#10B981" if is_online else "#EF4444"
    status_label = "Online" if is_online else "Offline"
    status_bg = "rgba(16, 185, 129, 0.15)" if is_online else "rgba(239, 68, 68, 0.15)"
    status_color = "#047857" if is_online else "#B91C1C"
    status_border = "rgba(16, 185, 129, 0.3)" if is_online else "rgba(239, 68, 68, 0.3)"

    with st.container(border=True):
        st.markdown(
            f"""<div id="civic-assistant-panel"></div>
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #CBD5E1; padding-bottom: 0.65rem; margin-bottom: 0.75rem;">
    <div style="display: flex; align-items: center; gap: 0.6rem;">
        <div style="width: 10px; height: 10px; background-color: {status_dot}; border-radius: 50%; box-shadow: 0 0 8px {status_dot};"></div>
        <span style="font-weight: 800; font-size: 1.02rem; color: #0F172A; letter-spacing: -0.01em;">NIRMAAN Civic Assistant</span>
    </div>
    <span style="font-size: 0.72rem; color: {status_color}; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; background: {status_bg}; border: 1px solid {status_border}; padding: 0.2rem 0.6rem; border-radius: 9999px;">{status_label}</span>
</div>""",
            unsafe_allow_html=True
        )

        # Chat messages history (rendered via native st.chat_message)
        chat_container = st.container()
        with chat_container:
            for idx, msg in enumerate(st.session_state["assistant_history"][-3:]):
                if msg["sender"] == "user":
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(msg["text"])
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        render_assistant_content(msg["text"])
                        if msg.get("action"):
                            act = msg["action"]
                            lbl = msg.get("action_label", "Proceed")
                            if st.button(lbl, key=f"asst_action_{idx}", type="primary", use_container_width=True):
                                if act == "navigate_report":
                                    st.session_state["nav_page"] = "Report Garbage"
                                elif act == "navigate_map":
                                    st.session_state["nav_page"] = "Live Map"
                                elif act in ["navigate_dossier", "view_dossier"]:
                                    st.session_state["nav_page"] = "Track Report"
                                    if msg.get("report_uid"):
                                        st.session_state["selected_report_uid"] = msg["report_uid"]
                                elif act in ["navigate_queue", "navigate_dashboard"]:
                                    st.session_state["nav_page"] = "Analytics"
                                st.rerun()

        # Suggested inquiries chips
        st.markdown(
            "<div style='font-size: 0.72rem; color: #475569; margin: 0.4rem 0 0.35rem 0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;'>Suggested Inquiries:</div>",
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("How to Report?", key="chip_report", use_container_width=True):
                _handle_user_prompt("How do I report a garbage hotspot?", repo)
            if st.button("Track a Report", key="chip_track", use_container_width=True):
                _handle_user_prompt("Track my report", repo)
        with c2:
            if st.button("Show Hotspot Map", key="chip_map", use_container_width=True):
                _handle_user_prompt("Show hotspot map", repo)
            if st.button("Priority Formula", key="chip_prio", use_container_width=True):
                _handle_user_prompt("How is cleanup priority calculated?", repo)

        # Message input & Send
        with st.form("assistant_chat_form", clear_on_submit=True):
            col_in, col_btn = st.columns([3.2, 1])
            with col_in:
                user_input = st.text_input(
                    "Message",
                    placeholder="Ask assistant or enter report ID...",
                    label_visibility="collapsed"
                )
            with col_btn:
                submitted = st.form_submit_button("Send", use_container_width=True)

            if submitted and user_input.strip():
                _handle_user_prompt(user_input.strip(), repo)


def _handle_user_prompt(prompt: str, repo: Repository):
    """Processes user prompt and appends to assistant history."""
    st.session_state["assistant_history"].append({"sender": "user", "text": prompt})
    try:
        res = process_assistant_query(prompt, repo)
        st.session_state["assistant_history"].append({
            "sender": "assistant",
            "text": res["response"],
            "action": res.get("action"),
            "action_label": res.get("action_label"),
            "report_uid": res.get("report_uid")
        })
    except Exception as e:
        st.session_state["assistant_history"].append({
            "sender": "assistant",
            "text": f"Error consulting civic service: {str(e)}",
            "action": None
        })
    st.rerun()
