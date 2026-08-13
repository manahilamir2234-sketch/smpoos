"""
SMPOOS Location CRUD Callbacks
Handles all location-related operations.
"""

from dash import Input, Output, State, ctx
import dash


def register_location_callbacks(app, system):
    """
    Register location CRUD callbacks with the Dash app.

    Args:
        app: Dash application instance
        system: SMPOOS system instance
    """

    @app.callback(
        Output("add-loc-modal", "is_open"),
        [Input("open-modal-btn", "n_clicks"),
         Input("submit-new-loc", "n_clicks")],
        [State("add-loc-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_add_loc_modal(n_open, n_submit, is_open):
        """Toggle the Add Location modal."""
        trigger = ctx.triggered_id
        if trigger == "open-modal-btn":
            return True
        if trigger == "submit-new-loc":
            return False
        return is_open

    @app.callback(
        Output("edit-loc-modal", "is_open"),
        [Input("edit-loc-btn", "n_clicks"),
         Input("submit-edit-loc", "n_clicks")],
        [State("edit-loc-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_edit_loc_modal(n_open, n_submit, is_open):
        """Toggle the Edit Location modal."""
        trigger = ctx.triggered_id
        if trigger == "edit-loc-btn":
            return True
        if trigger == "submit-edit-loc":
            return False
        return is_open

    @app.callback(
        Output("delete-loc-modal", "is_open"),
        [Input("delete-loc-btn", "n_clicks"),
         Input("confirm-delete-loc", "n_clicks"),
         Input("cancel-delete-loc", "n_clicks")],
        [State("delete-loc-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_delete_loc_modal(n_open, n_confirm, n_cancel, is_open):
        """Toggle the Delete Location confirmation modal."""
        trigger = ctx.triggered_id
        if trigger == "delete-loc-btn":
            return True
        if trigger in ("confirm-delete-loc", "cancel-delete-loc"):
            return False
        return is_open

    @app.callback(
        Output("asset-table", "data"),
        Input("submit-new-loc", "n_clicks"),
        [State("new-loc-id", "value"),
         State("new-loc-name", "value"),
         State("new-loc-type", "value"),
         State("new-loc-status", "value"),
         State("new-loc-capacity", "value"),
         State("active-role", "data")],
        prevent_initial_call=True
    )
    def handle_add_location(n, lid, name, ltype, status, cap, role):
        """Create a new location."""
        from src.utils.rbac_utils import can_modify_data
        if n and lid and name and can_modify_data(role or "Harbourmaster"):
            system.add_location(lid, name, ltype or "Berth",
                                status or "Active", cap or 0)
        return system.get_locations_df().to_dict('records')

    @app.callback(
        [Output("edit-loc-id", "value"),
         Output("edit-loc-name", "value"),
         Output("edit-loc-type", "value"),
         Output("edit-loc-status", "value"),
         Output("edit-loc-capacity", "value")],
        Input("asset-table", "selected_rows"),
        State("asset-table", "data"),
        prevent_initial_call=True
    )
    def populate_edit_loc_form(selected_rows, data):
        """Populate the edit location form with selected row data."""
        if selected_rows and data:
            row = data[selected_rows[0]]
            return (
                row.get('location_id', ''),
                row.get('name', ''),
                row.get('type', ''),
                row.get('status', ''),
                row.get('capacity_tonnes', 0)
            )
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output("asset-table", "data", allow_duplicate=True),
        Input("submit-edit-loc", "n_clicks"),
        [State("edit-loc-id", "value"),
         State("edit-loc-name", "value"),
         State("edit-loc-type", "value"),
         State("edit-loc-status", "value"),
         State("edit-loc-capacity", "value"),
         State("active-role", "data")],
        prevent_initial_call=True
    )
    def handle_update_location(n, lid, name, ltype, status, cap, role):
        """Update an existing location."""
        from src.utils.rbac_utils import can_modify_data
        if n and lid and can_modify_data(role or "Harbourmaster"):
            system.update_location(
                lid, name=name, loc_type=ltype, status=status, capacity=cap)
        return system.get_locations_df().to_dict('records')

    @app.callback(
        Output("asset-table", "data", allow_duplicate=True),
        Input("confirm-delete-loc", "n_clicks"),
        State("asset-table", "selected_rows"),
        State("asset-table", "data"),
        State("active-role", "data"),
        prevent_initial_call=True
    )
    def handle_delete_location(n, selected_rows, data, role):
        """Delete the selected location."""
        from src.utils.rbac_utils import can_modify_data
        if n and selected_rows and data and can_modify_data(role or "Harbourmaster"):
            row = data[selected_rows[0]]
            lid = row.get('location_id')
            if lid:
                system.delete_location(lid)
        return system.get_locations_df().to_dict('records')

    @app.callback(
        Output("asset-table", "data", allow_duplicate=True),
        Input("asset-search", "value"),
        prevent_initial_call=True
    )
    def filter_assets(search_value):
        """Filter the asset table based on search input."""
        df = system.get_locations_df()
        if search_value:
            search_lower = search_value.lower()
            mask = (
                df['location_id'].astype(str).str.lower().str.contains(search_lower, na=False) |
                df['name'].astype(str).str.lower().str.contains(search_lower, na=False) |
                df['type'].astype(str).str.lower().str.contains(search_lower, na=False) |
                df['status'].astype(str).str.lower(
                ).str.contains(search_lower, na=False)
            )
            df = df[mask]
        return df.to_dict('records')

    @app.callback(
        [Output("edit-loc-btn", "disabled"),
         Output("delete-loc-btn", "disabled")],
        Input("asset-table", "selected_rows")
    )
    def update_loc_button_states(selected_rows):
        """Enable/disable edit and delete buttons based on selection."""
        disabled = not (selected_rows and len(selected_rows) > 0)
        return disabled, disabled
