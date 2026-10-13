"""
NIRMAAN AI - Civic Audit Trail View
Provides an immutable chronological log of system state changes, task dispatches,
priority overrides, and verification approvals (Feature 5).
"""

import streamlit as st
import pandas as pd
from src.database.repository import Repository
from src.ui.components import render_header


from src.auth.rbac import has_permission


def render(repo: Repository):
    if not has_permission("view_audit_logs"):
        st.error("Access Restricted: Immutable civic audit trails are restricted to Administrators.")
        st.info("Please switch to an Administrator profile via the Login / Role Switcher to inspect the audit log.")
        return

    render_header(
        title="Immutable Civic Audit Trail",
        subtitle="Chronological log of operational changes, priority overrides, and supervisory sign-offs.",
        active_tab="Audit Trail"
    )

    logs = repo.get_audit_logs(limit=150)
    if not logs:
        st.info("No audit logs recorded.")
        return

    st.markdown(
        f"""
        <div class="neu-card">
            <span style="font-size: 0.88rem; color: #475569;">
                Displaying the latest <strong>{len(logs)} audit entries</strong>.
                Entries are permanently recorded for civic transparency.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Search & Filter
    search = st.text_input("Filter by Action or Ticket ID", placeholder="e.g. OVERRIDE, TASK, REP-BLR")
    filtered = logs
    if search:
        s_low = search.lower()
        filtered = [l for l in logs if s_low in l["action"].lower() or s_low in str(l["entity_id"]).lower() or s_low in l["user_name"].lower()]

    if filtered:
        df = pd.DataFrame(filtered)
        display_df = df[["created_at", "user_name", "action", "entity_type", "entity_id", "old_value", "new_value"]].rename(
            columns={
                "created_at": "Timestamp",
                "user_name": "Officer / Actor",
                "action": "Action Code",
                "entity_type": "Entity",
                "entity_id": "Target ID",
                "old_value": "Previous State",
                "new_value": "New State"
            }
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No logs matched your filter.")
