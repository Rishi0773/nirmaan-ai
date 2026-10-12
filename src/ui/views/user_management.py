"""
NIRMAAN AI - User & Role Management View
Facilitates seamless role switching between Administrator, Ward Officer,
Sanitation Supervisor, Cleanup Worker, and Citizen (Feature 5 & RBAC).
"""

import streamlit as st
from src.database.repository import Repository
from src.auth.rbac import get_current_user, set_current_user, ROLE_PERMISSIONS
from src.ui.components import render_header


def render(repo: Repository):
    render_header(
        title="Civic User & Role Management",
        subtitle="Manage municipal personnel, switch simulation roles, and inspect permission boundaries.",
        active_tab="User Management"
    )

    current = get_current_user()
    users = repo.get_users()

    col1, col2 = st.columns([1.2, 2])

    with col1:
        st.markdown(
            f"""
            <div class="neu-card">
                <h4 style="margin-top: 0; color: #0F172A;">Active Session Profile</h4>
                <div style="font-size: 1.1rem; font-weight: 700; color: #059669;">{current['full_name']}</div>
                <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 0.75rem;">Username: @{current['username']}</div>
                <div style="font-size: 0.88rem; color: #1E293B;">Role: <strong>{current['role']}</strong></div>
                <div style="font-size: 0.88rem; color: #1E293B;">Assigned Ward: <strong>{current.get('ward_assigned') or 'All Wards'}</strong></div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### Switch Active Role (Demonstration)")
        user_names = [f"{u['full_name']} ({u['role']})" for u in users]
        current_idx = 0
        for i, u in enumerate(users):
            if u["username"] == current["username"]:
                current_idx = i
                break

        selected_user_str = st.selectbox("Select User Identity", options=user_names, index=current_idx)
        if st.button("Switch Active User", type="primary", use_container_width=True):
            target_user = users[user_names.index(selected_user_str)]
            set_current_user(target_user)
            st.success(f"Switched identity to {target_user['full_name']} ({target_user['role']}).")
            st.rerun()

    with col2:
        st.markdown("### Role Permission Boundaries")
        role_selected = st.selectbox("Inspect Permissions for Role", options=list(ROLE_PERMISSIONS.keys()))
        perms = ROLE_PERMISSIONS[role_selected]

        st.markdown(
            f"""
            <div class="neu-card">
                <div style="font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;">
                    Capabilities Granted to {role_selected}:
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">
                    {''.join([f'<span style="background: #F1F5F9; border: 1px solid #CBD5E1; color: #334155; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.78rem;">✓ {p.replace("_", " ").title()}</span>' for p in perms])}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### Registered System Officers")
        user_table = [
            {"Name": u["full_name"], "Role": u["role"], "Ward": u.get("ward_assigned", "All"), "Email": u["email"]}
            for u in users
        ]
        st.table(user_table)
