"""
NIRMAAN AI - Floating Civic Assistant Component
Interactive civic guidance, rule-based decision support,
and real SQLite report tracking with high-contrast readable styling.
"""

import streamlit as st
from src.database.repository import Repository
from services.assistant_service import process_assistant_query


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
<style>
div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) {{
    background: rgba(255, 255, 255, 0.94) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.90) !important;
    border-radius: 18px !important;
    padding: 1.25rem 1.25rem 1.1rem 1.25rem !important;
    box-shadow: 0 20px 45px rgba(5, 11, 26, 0.38) !important;
    color: #0F172A !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) p,
div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) span,
div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) label {{
    color: #0F172A !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) button {{
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
}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) button:hover {{
    background: #F1F5F9 !important;
    border-color: #94A3B8 !important;
    color: #0F172A !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) button[kind="primary"] {{
    background: #0D9488 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 700 !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) input {{
    background: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(#civic-assistant-panel) input::placeholder {{
    color: #94A3B8 !important;
}}
</style>

<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; padding-bottom: 0.65rem; margin-bottom: 0.75rem;">
    <div style="display: flex; align-items: center; gap: 0.6rem;">
        <div style="width: 10px; height: 10px; background-color: {status_dot}; border-radius: 50%; box-shadow: 0 0 8px {status_dot};"></div>
        <span style="font-weight: 800; font-size: 1.02rem; color: #0F172A; letter-spacing: -0.01em;">NIRMAAN Civic Assistant</span>
    </div>
    <span style="font-size: 0.72rem; color: {status_color}; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; background: {status_bg}; border: 1px solid {status_border}; padding: 0.2rem 0.6rem; border-radius: 9999px;">{status_label}</span>
</div>""",
            unsafe_allow_html=True
        )

        # Chat messages history (internal scrolling, high contrast)
        chat_container = st.container()
        with chat_container:
            for idx, msg in enumerate(st.session_state["assistant_history"][-3:]):
                if msg["sender"] == "user":
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: flex-end; margin-bottom: 0.55rem;">
                            <div style="background: linear-gradient(135deg, #0D9488 0%, #059669 100%); color: #FFFFFF !important; padding: 0.5rem 0.85rem; border-radius: 10px; font-size: 0.83rem; font-weight: 500; max-width: 85%; box-shadow: 0 3px 10px rgba(5, 150, 105, 0.25);">
                                {msg['text']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    clean_msg = msg['text'].replace('\n', '<br/>')
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: flex-start; margin-bottom: 0.55rem;">
                            <div style="background: #F1F5F9; border: 1px solid #CBD5E1; color: #0F172A !important; padding: 0.65rem 0.9rem; border-radius: 10px; font-size: 0.83rem; line-height: 1.5; max-width: 95%; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                                {clean_msg}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if msg.get("action"):
                        act = msg["action"]
                        lbl = msg.get("action_label", "Proceed")
                        if st.button(lbl, key=f"asst_action_{idx}", use_container_width=True):
                            if act == "navigate_report":
                                st.session_state["nav_page"] = "Report Garbage"
                            elif act == "navigate_map":
                                st.session_state["nav_page"] = "Live Map"
                            elif act == "navigate_dossier" or act == "view_dossier":
                                st.session_state["nav_page"] = "Track Report"
                                if msg.get("report_uid"):
                                    st.session_state["selected_report_uid"] = msg["report_uid"]
                            elif act == "navigate_queue":
                                st.session_state["nav_page"] = "Analytics"
                            elif act == "navigate_dashboard":
                                st.session_state["nav_page"] = "Analytics"
                            st.rerun()

        # Suggested inquiries chips
        st.markdown(
            "<div style='font-size: 0.72rem; color: #64748B; margin: 0.4rem 0 0.35rem 0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;'>Suggested Questions:</div>",
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("How do I report?", key="chip_report", use_container_width=True):
                _handle_user_prompt("How do I report a garbage hotspot?", repo)
            if st.button("Track my report", key="chip_track", use_container_width=True):
                _handle_user_prompt("Track my report", repo)
        with c2:
            if st.button("Show hotspot map", key="chip_map", use_container_width=True):
                _handle_user_prompt("Show hotspot map", repo)
            if st.button("Priority formula?", key="chip_prio", use_container_width=True):
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

