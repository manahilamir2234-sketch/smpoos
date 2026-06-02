"""
SMPOOS Notification CRUD Callbacks
Handles all notification-related operations.
"""

from dash import Input, Output, State, ctx


def register_notification_callbacks(app, system):
    """Register notification CRUD callbacks with the Dash app."""

    @app.callback(
        Output("add-notif-modal", "is_open"),
        [Input("open-notif-modal-btn", "n_clicks"),
         Input("submit-new-notif", "n_clicks")],
        [State("add-notif-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_add_notif_modal(n_open, n_submit, is_open):
        trigger = ctx.triggered_id
        if trigger == "open-notif-modal-btn":
            return True
        if trigger == "submit-new-notif":
            return False
        return is_open

    @app.callback(
        Output("delete-notif-modal", "is_open"),
        [Input("delete-notif-btn", "n_clicks"),
         Input("confirm-delete-notif", "n_clicks"),
         Input("cancel-delete-notif", "n_clicks")],
        [State("delete-notif-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_delete_notif_modal(n_open, n_confirm, n_cancel, is_open):
        trigger = ctx.triggered_id
        if trigger == "delete-notif-btn":
            return True
        if trigger in ("confirm-delete-notif", "cancel-delete-notif"):
            return False
        return is_open

    @app.callback(
        Output("notif-table", "data"),
        Input("submit-new-notif", "n_clicks"),
        [State("new-notif-id", "value"),
         State("new-notif-type", "value"),
         State("new-notif-location", "value"),
         State("new-notif-severity", "value"),
         State("new-notif-message", "value")],
        prevent_initial_call=True
    )
    def handle_add_notification(n, nid, alert_type, location_id, severity, message):
        if n and nid and message:
            system.add_notification(
                nid, alert_type or "Equipment Failure", location_id or "", severity or "Medium", message)
        return system.get_notifications_df().to_dict('records')

    @app.callback(
        Output("notif-table", "data", allow_duplicate=True),
        Input("confirm-delete-notif", "n_clicks"),
        State("notif-table", "selected_rows"),
        State("notif-table", "data"),
        prevent_initial_call=True
    )
    def handle_delete_notification(n, selected_rows, data):
        if n and selected_rows and data:
            row = data[selected_rows[0]]
            nid = row.get('notification_id')
            if nid:
                system.delete_notification(nid)
        return system.get_notifications_df().to_dict('records')

    @app.callback(
        [Output("acknowledge-notif-btn", "disabled"),
         Output("delete-notif-btn", "disabled")],
        Input("notif-table", "selected_rows")
    )
    def update_notif_button_states(selected_rows):
        disabled = not (selected_rows and len(selected_rows) > 0)
        return disabled, disabled

    @app.callback(
        Output("notif-table", "data", allow_duplicate=True),
        Input("notif-severity-filter", "value"),
        prevent_initial_call=True
    )
    def filter_notifications_by_severity(severity):
        df = system.get_notifications_df()
        if severity and severity != "all":
            df = df[df['severity'] == severity]
        return df.to_dict('records')
