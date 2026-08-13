"""
Role-based access helpers for SMPOOS.
Defines which roles may change operational data and which alert
severities each role typically sees on the dashboard.
"""

# Roles that may create, update or delete operational records.
ADMIN_ROLES = {
    "Harbourmaster",
    "Administrator",
    "Operations Supervisor",
    "Safety Officer",
}

# Default severity filter applied when a role is selected.
ROLE_SEVERITY_FOCUS = {
    "Harbourmaster": None,  # all severities
    "Administrator": None,
    "Operations Supervisor": ["Critical", "High", "Medium"],
    "Safety Officer": ["Critical", "High"],
    "Crane Operator": ["Critical", "High"],
    "Stevedore": ["Critical", "High", "Medium"],
}


def can_modify_data(role: str) -> bool:
    """Return True if the active role is allowed to change port data."""
    return role in ADMIN_ROLES


def severities_for_role(role: str):
    """
    Return the list of severities that should be shown for a role,
    or None when the role should see every severity.
    """
    return ROLE_SEVERITY_FOCUS.get(role)
