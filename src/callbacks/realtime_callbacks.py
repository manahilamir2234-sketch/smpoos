"""
SMPOOS Real-Time Simulation Callbacks
Handles auto-refresh, live data simulation, and audit log refresh.
"""

from dash import Input, Output, State, html
import dash
import random
from src.utils import simulation_utils
from src.utils.rbac_utils import severities_for_role


def register_realtime_callbacks(app, system):
    """Register real-time simulation callbacks with the Dash app."""

    @app.callback(
        [Output("overview-alert-table", "data"),
         Output("stat-berth-occupancy", "children"),
         Output("stat-active-routes", "children"),
         Output("stat-critical-alerts", "children"),
         Output("audit-log-section", "children"),
         Output("stat-wind", "children"),
         Output("stat-tide", "children"),
         Output("stat-visibility", "children"),
         Output("stat-incoming-vessels", "children")],
        [Input("realtime-interval", "n_intervals"),
         Input("active-role", "data")]
    )
    def auto_refresh_dashboard(n_intervals, active_role):
        """Auto-refresh dashboard metrics, alerts, env widgets and audit log."""
        audit_entries = system.get_audit_log()[-8:]
        if audit_entries:
            audit_children = [
                html.P(
                    f"{e['timestamp'][:19]} | {e['action']} {e['entity_type']} "
                    f"{e['entity_id']} — {e['details']}"
                )
                for e in reversed(audit_entries)
            ]
        else:
            audit_children = [
                html.P("No administrative actions recorded yet.")
            ]

        if n_intervals is not None and n_intervals > 0:
            if random.random() < 0.2:
                new_notif = simulation_utils.generate_random_notification(system)
                if new_notif:
                    system.add_notification(
                        new_notif['notification_id'],
                        new_notif['alert_type'],
                        new_notif['location_id'],
                        new_notif['severity'],
                        new_notif['message'],
                        new_notif['timestamp']
                    )

        updated_notifs = system.get_notifications_df()
        updated_locations = system.get_locations_df()
        updated_routes = system.get_routes_df()

        allowed = severities_for_role(active_role or "Harbourmaster")
        if allowed is not None and not updated_notifs.empty:
            updated_notifs = updated_notifs[
                updated_notifs['severity'].isin(allowed)
            ]

        active_berths = len(
            updated_locations[updated_locations['status'] == 'Active'])
        total_berths = len(updated_locations)
        active_routes_count = len(
            updated_routes[updated_routes['status'] == 'Open'])
        critical_alerts = len(
            updated_notifs[updated_notifs['severity'] == 'Critical'])

        notif_data = updated_notifs.sort_values(
            'timestamp', ascending=False).head(10).to_dict('records')

        return (
            notif_data,
            f"{active_berths}/{total_berths}",
            str(active_routes_count),
            str(critical_alerts),
            audit_children,
            f"{random.uniform(4, 22):.1f}",
            f"{random.uniform(0.4, 3.2):.2f}",
            f"{random.uniform(2, 12):.1f}",
            str(random.randint(8, 18)),
        )

    @app.callback(
        Output("acknowledge-alert-btn", "disabled"),
        Input("overview-alert-table", "selected_rows")
    )
    def toggle_overview_ack(selected_rows):
        return not (selected_rows and len(selected_rows) > 0)

    @app.callback(
        Output("overview-alert-table", "data", allow_duplicate=True),
        Input("acknowledge-alert-btn", "n_clicks"),
        State("overview-alert-table", "selected_rows"),
        State("overview-alert-table", "data"),
        State("active-role", "data"),
        prevent_initial_call=True
    )
    def acknowledge_overview_alert(n, selected_rows, data, role):
        from src.utils.rbac_utils import can_modify_data, severities_for_role
        if n and selected_rows and data and can_modify_data(role or "Harbourmaster"):
            row = data[selected_rows[0]]
            nid = row.get("notification_id")
            msg = row.get("message", "")
            if nid and not str(msg).startswith("[ACK]"):
                system.update_notification(nid, message=f"[ACK] {msg}")
        df = system.get_notifications_df()
        allowed = severities_for_role(role or "Harbourmaster")
        if allowed is not None and not df.empty:
            df = df[df["severity"].isin(allowed)]
        return df.sort_values("timestamp", ascending=False).head(10).to_dict("records")
