"""
Callbacks that apply role-based filtering.
Write permission checks are enforced inside CRUD callbacks via active-role store.
"""

from dash import Input, Output


def register_rbac_callbacks(app, system):
    """Register RBAC-related Dash callbacks."""

    @app.callback(
        Output("active-role", "data"),
        Output("rbac-status-text", "children"),
        Input("role-selector", "value"),
    )
    def sync_active_role(role):
        role = role or "Harbourmaster"
        from src.utils.rbac_utils import can_modify_data

        mode = "write enabled" if can_modify_data(role) else "read-only"
        return role, f"Active role: {role} ({mode})"

    @app.callback(
        Output("notif-table", "data", allow_duplicate=True),
        Input("role-selector", "value"),
        Input("notif-severity-filter", "value"),
        prevent_initial_call=True,
    )
    def filter_notifications_by_role_and_severity(role, severity):
        """Combine role focus with the severity dropdown on Notifications page."""
        df = system.get_notifications_df()
        if df is None or df.empty:
            return []

        from src.utils.rbac_utils import severities_for_role

        allowed = severities_for_role(role or "Harbourmaster")
        if allowed is not None:
            df = df[df["severity"].isin(allowed)]
        if severity and severity != "all":
            df = df[df["severity"] == severity]
        return df.to_dict("records")
