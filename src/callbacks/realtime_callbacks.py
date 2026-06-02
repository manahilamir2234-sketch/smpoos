"""
SMPOOS Real-Time Simulation Callbacks
Handles auto-refresh and live data simulation.
"""

from dash import Input, Output
import dash
import random
from src.utils import simulation_utils


def register_realtime_callbacks(app, system):
    """Register real-time simulation callbacks with the Dash app."""

    @app.callback(
        [Output("overview-alert-table", "data"),
         Output("stat-berth-occupancy", "children"),
         Output("stat-active-routes", "children"),
         Output("stat-critical-alerts", "children")],
        Input("realtime-interval", "n_intervals")
    )
    def auto_refresh_dashboard(n_intervals):
        """
        Auto-refresh dashboard with simulated data every 5 seconds.

        Args:
            n_intervals: Number of interval triggers

        Returns:
            Updated notification data and metric values
        """
        if n_intervals is None or n_intervals == 0:
            return [dash.no_update] * 4

        # Simulate berth changes
        locations_df = simulation_utils.simulate_berth_occupancy_change(
            system.get_locations_df())

        # Simulate route changes
        routes_df = simulation_utils.simulate_route_traffic(
            system.get_routes_df())

        # Occasionally add new notification (30% chance)
        if random.random() < 0.3:
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

        # Refresh data
        updated_notifs = system.get_notifications_df()
        updated_locations = system.get_locations_df()
        updated_routes = system.get_routes_df()

        # Calculate metrics
        active_berths = len(
            updated_locations[updated_locations['status'] == 'Active'])
        total_berths = len(updated_locations)
        active_routes_count = len(
            updated_routes[updated_routes['status'] == 'Open'])
        critical_alerts = len(
            updated_notifs[updated_notifs['severity'] == 'Critical'])

        # Prepare notification data
        notif_data = updated_notifs.sort_values(
            'timestamp', ascending=False).head(10).to_dict('records')

        return (
            notif_data,
            f"{active_berths}/{total_berths}",
            str(active_routes_count),
            str(critical_alerts)
        )

    @app.callback(
        Output("analytics-charts-container", "children", allow_duplicate=True),
        Input("realtime-interval", "n_intervals"),
        prevent_initial_call=True
    )
    def update_analytics_on_refresh(n_intervals):
        """Trigger analytics refresh (handled by analytics page on navigation)."""
        return dash.no_update
