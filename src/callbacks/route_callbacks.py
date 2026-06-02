"""
SMPOOS Route CRUD Callbacks
Handles all route-related operations.
"""

from dash import Input, Output, State, ctx
import dash


def register_route_callbacks(app, system):
    """Register route CRUD callbacks with the Dash app."""

    @app.callback(
        Output("add-route-modal", "is_open"),
        [Input("open-route-modal-btn", "n_clicks"),
         Input("submit-new-route", "n_clicks")],
        [State("add-route-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_add_route_modal(n_open, n_submit, is_open):
        trigger = ctx.triggered_id
        if trigger == "open-route-modal-btn":
            return True
        if trigger == "submit-new-route":
            return False
        return is_open

    @app.callback(
        Output("edit-route-modal", "is_open"),
        [Input("edit-route-btn", "n_clicks"),
         Input("submit-edit-route", "n_clicks")],
        [State("edit-route-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_edit_route_modal(n_open, n_submit, is_open):
        trigger = ctx.triggered_id
        if trigger == "edit-route-btn":
            return True
        if trigger == "submit-edit-route":
            return False
        return is_open

    @app.callback(
        Output("delete-route-modal", "is_open"),
        [Input("delete-route-btn", "n_clicks"),
         Input("confirm-delete-route", "n_clicks"),
         Input("cancel-delete-route", "n_clicks")],
        [State("delete-route-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_delete_route_modal(n_open, n_confirm, n_cancel, is_open):
        trigger = ctx.triggered_id
        if trigger == "delete-route-btn":
            return True
        if trigger in ("confirm-delete-route", "cancel-delete-route"):
            return False
        return is_open

    @app.callback(
        Output("route-table", "data"),
        Input("submit-new-route", "n_clicks"),
        [State("new-route-id", "value"),
         State("new-route-start", "value"),
         State("new-route-end", "value"),
         State("new-route-type", "value"),
         State("new-route-distance", "value"),
         State("new-route-status", "value")],
        prevent_initial_call=True
    )
    def handle_add_route(n, rid, start, end, rtype, distance, status):
        if n and rid and start and end:
            system.add_route(
                rid, start, end, rtype or "Shipping Lane", distance or 0, status or "Open")
        return system.get_routes_df().to_dict('records')

    @app.callback(
        [Output("edit-route-id", "value"),
         Output("edit-route-start", "value"),
         Output("edit-route-end", "value"),
         Output("edit-route-type", "value"),
         Output("edit-route-distance", "value"),
         Output("edit-route-status", "value")],
        Input("route-table", "selected_rows"),
        State("route-table", "data"),
        prevent_initial_call=True
    )
    def populate_edit_route_form(selected_rows, data):
        if selected_rows and data:
            row = data[selected_rows[0]]
            return (
                row.get('route_id', ''),
                row.get('start_location', ''),
                row.get('end_location', ''),
                row.get('route_type', ''),
                row.get('distance_km', 0),
                row.get('status', '')
            )
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output("route-table", "data", allow_duplicate=True),
        Input("submit-edit-route", "n_clicks"),
        [State("edit-route-id", "value"),
         State("edit-route-start", "value"),
         State("edit-route-end", "value"),
         State("edit-route-type", "value"),
         State("edit-route-distance", "value"),
         State("edit-route-status", "value")],
        prevent_initial_call=True
    )
    def handle_update_route(n, rid, start, end, rtype, distance, status):
        if n and rid:
            system.update_route(rid, start_location=start, end_location=end,
                                route_type=rtype, distance_km=distance, status=status)
        return system.get_routes_df().to_dict('records')

    @app.callback(
        Output("route-table", "data", allow_duplicate=True),
        Input("confirm-delete-route", "n_clicks"),
        State("route-table", "selected_rows"),
        State("route-table", "data"),
        prevent_initial_call=True
    )
    def handle_delete_route(n, selected_rows, data):
        if n and selected_rows and data:
            row = data[selected_rows[0]]
            rid = row.get('route_id')
            if rid:
                system.delete_route(rid)
        return system.get_routes_df().to_dict('records')

    @app.callback(
        [Output("edit-route-btn", "disabled"),
         Output("delete-route-btn", "disabled")],
        Input("route-table", "selected_rows")
    )
    def update_route_button_states(selected_rows):
        disabled = not (selected_rows and len(selected_rows) > 0)
        return disabled, disabled
