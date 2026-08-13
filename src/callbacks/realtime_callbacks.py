"""
SMPOOS Real-Time Simulation Callbacks
Handles auto-refresh, live data simulation, and audit log refresh.
"""

from dash import Input, Output, html
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
         Output("audit-log-section", "children")],
        [Input("realtime-interval", "n_intervals"),
         Input("active-role", "data")]
    )
    def auto_refresh_dashboard(n_intervals, active_role):
        """Auto-refresh dashboard metrics, alerts and audit log."""
        # Always rebuild audit entries so the placeholder is never left empty
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

        if n_intervals is None or n_intervals == 0:
            updated_notifs = system.get_notifications_df()
            updated_locations = system.get_locations_df()
            updated_routes = system.get_routes_df()
        else:
            # Simulation for demo of real-time monitoring (brief requirement)
            simulation_utils.simulate_berth_occupancy_change(
                system.get_locations_df())
            simulation_utils.simulate_route_traffic(system.get_routes_df())

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
            audit_children
        )
