"""
NIRMAAN AI - Role-Based Access Control (RBAC)
Defines user roles and permissions across civic administrative workflows.
"""

from typing import Dict, List, Any
import streamlit as st

# Role hierarchy and permissions
ROLE_PERMISSIONS = {
    "Administrator": [
        "view_dashboard", "report_incident", "view_reports", "view_map",
        "view_hotspots", "view_priority_queue", "manage_tasks", "verify_cleanup",
        "tune_weights", "view_analytics", "export_reports", "manage_users",
        "view_audit_logs", "reopen_case"
    ],
    "Ward Officer": [
        "view_dashboard", "report_incident", "view_reports", "view_map",
        "view_hotspots", "view_priority_queue", "manage_tasks", "verify_cleanup",
        "view_analytics", "export_reports", "reopen_case"
    ],
    "Sanitation Supervisor": [
        "view_dashboard", "report_incident", "view_reports", "view_map",
        "view_hotspots", "view_priority_queue", "manage_tasks", "verify_cleanup",
        "view_analytics"
    ],
    "Cleanup Worker": [
        "view_dashboard", "view_reports", "view_map", "manage_tasks",
        "submit_evidence"
    ],
    "Citizen": [
        "view_dashboard", "report_incident", "view_reports", "view_map"
    ]
}

ROLES = list(ROLE_PERMISSIONS.keys())


def get_current_user() -> Dict[str, Any]:
    """Returns the currently active session user or defaults to Administrator for demo convenience."""
    if "current_user" not in st.session_state:
        st.session_state.current_user = {
            "id": 1,
            "username": "admin_blr",
            "full_name": "Dr. Ramesh Kumar (Admin)",
            "role": "Administrator",
            "ward_assigned": "Central"
        }
    return st.session_state.current_user


def set_current_user(user: Dict[str, Any]):
    """Switches the active user role."""
    st.session_state.current_user = user


def has_permission(permission: str) -> bool:
    """Checks whether active session user holds the requested permission."""
    user = get_current_user()
    role = user.get("role", "Citizen")
    allowed = ROLE_PERMISSIONS.get(role, [])
    return permission in allowed
