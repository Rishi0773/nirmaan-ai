"""
NIRMAAN AI - Unit Tests: Role-Based Access Control
"""

import pytest
from src.auth.rbac import ROLE_PERMISSIONS


def test_rbac_roles_integrity():
    assert "Administrator" in ROLE_PERMISSIONS
    assert "Citizen" in ROLE_PERMISSIONS
    assert "Sanitation Supervisor" in ROLE_PERMISSIONS

    # Citizens can report but not tune weights or verify
    citizen_perms = ROLE_PERMISSIONS["Citizen"]
    assert "report_incident" in citizen_perms
    assert "tune_weights" not in citizen_perms
    assert "verify_cleanup" not in citizen_perms

    # Administrator has full permissions
    admin_perms = ROLE_PERMISSIONS["Administrator"]
    assert "tune_weights" in admin_perms
    assert "verify_cleanup" in admin_perms
    assert "manage_users" in admin_perms
