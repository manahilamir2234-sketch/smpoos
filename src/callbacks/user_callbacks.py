"""
SMPOOS User CRUD Callbacks
Handles all user-related operations.
"""

from dash import Input, Output, State, ctx
import dash


def register_user_callbacks(app, system):
    """Register user CRUD callbacks with the Dash app."""

    @app.callback(
        Output("add-user-modal", "is_open"),
        [Input("open-user-modal-btn", "n_clicks"),
         Input("submit-new-user", "n_clicks")],
        [State("add-user-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_add_user_modal(n_open, n_submit, is_open):
        trigger = ctx.triggered_id
        if trigger == "open-user-modal-btn":
            return True
        if trigger == "submit-new-user":
            return False
        return is_open

    @app.callback(
        Output("edit-user-modal", "is_open"),
        [Input("edit-user-btn", "n_clicks"),
         Input("submit-edit-user", "n_clicks")],
        [State("edit-user-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_edit_user_modal(n_open, n_submit, is_open):
        trigger = ctx.triggered_id
        if trigger == "edit-user-btn":
            return True
        if trigger == "submit-edit-user":
            return False
        return is_open

    @app.callback(
        Output("delete-user-modal", "is_open"),
        [Input("delete-user-btn", "n_clicks"),
         Input("confirm-delete-user", "n_clicks"),
         Input("cancel-delete-user", "n_clicks")],
        [State("delete-user-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_delete_user_modal(n_open, n_confirm, n_cancel, is_open):
        trigger = ctx.triggered_id
        if trigger == "delete-user-btn":
            return True
        if trigger in ("confirm-delete-user", "cancel-delete-user"):
            return False
        return is_open

    @app.callback(
        Output("user-table", "data"),
        Input("submit-new-user", "n_clicks"),
        [State("new-user-id", "value"),
         State("new-user-name", "value"),
         State("new-user-role", "value"),
         State("new-user-email", "value"),
         State("new-user-active", "value"),
         State("active-role", "data")],
        prevent_initial_call=True
    )
    def handle_add_user(n, uid, name, role, email, active, active_role):
        from src.utils.rbac_utils import can_modify_data
        if n and uid and name and can_modify_data(active_role or "Harbourmaster"):
            system.add_user(uid, name, role or "Harbourmaster",
                            email or "", active or "Yes")
        return system.get_users_df().to_dict('records')

    @app.callback(
        [Output("edit-user-id", "value"),
         Output("edit-user-name", "value"),
         Output("edit-user-role", "value"),
         Output("edit-user-email", "value"),
         Output("edit-user-active", "value")],
        Input("user-table", "selected_rows"),
        State("user-table", "data"),
        prevent_initial_call=True
    )
    def populate_edit_user_form(selected_rows, data):
        if selected_rows and data:
            row = data[selected_rows[0]]
            return (
                row.get('user_id', ''),
                row.get('name', ''),
                row.get('role', ''),
                row.get('email', ''),
                row.get('active', 'Yes')
            )
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output("user-table", "data", allow_duplicate=True),
        Input("submit-edit-user", "n_clicks"),
        [State("edit-user-id", "value"),
         State("edit-user-name", "value"),
         State("edit-user-role", "value"),
         State("edit-user-email", "value"),
         State("edit-user-active", "value"),
         State("active-role", "data")],
        prevent_initial_call=True
    )
    def handle_update_user(n, uid, name, role, email, active, active_role):
        from src.utils.rbac_utils import can_modify_data
        if n and uid and can_modify_data(active_role or "Harbourmaster"):
            system.update_user(uid, name=name, role=role,
                               email=email, active=active)
        return system.get_users_df().to_dict('records')

    @app.callback(
        Output("user-table", "data", allow_duplicate=True),
        Input("confirm-delete-user", "n_clicks"),
        State("user-table", "selected_rows"),
        State("user-table", "data"),
        State("active-role", "data"),
        prevent_initial_call=True
    )
    def handle_delete_user(n, selected_rows, data, active_role):
        from src.utils.rbac_utils import can_modify_data
        if n and selected_rows and data and can_modify_data(active_role or "Harbourmaster"):
            row = data[selected_rows[0]]
            uid = row.get('user_id')
            if uid:
                system.delete_user(uid)
        return system.get_users_df().to_dict('records')

    @app.callback(
        [Output("edit-user-btn", "disabled"),
         Output("delete-user-btn", "disabled"),
         Output("export-user-btn", "disabled"),
         Output("erase-user-btn", "disabled")],
        Input("user-table", "selected_rows")
    )
    def update_user_button_states(selected_rows):
        disabled = not (selected_rows and len(selected_rows) > 0)
        return disabled, disabled, disabled, disabled

    @app.callback(
        Output("gdpr-export-output", "children"),
        Input("export-user-btn", "n_clicks"),
        State("user-table", "selected_rows"),
        State("user-table", "data"),
        State("active-role", "data"),
        prevent_initial_call=True
    )
    def handle_export_user(n, selected_rows, data, active_role):
        from src.utils.rbac_utils import can_modify_data
        from dash import html
        if not n or not selected_rows or not data:
            return ""
        if not can_modify_data(active_role or "Harbourmaster"):
            return html.P("Export refused: active role is read-only.")
        uid = data[selected_rows[0]].get("user_id")
        payload = system.export_user_data(uid)
        return html.Pre(str(payload))

    @app.callback(
        Output("user-table", "data", allow_duplicate=True),
        Output("gdpr-export-output", "children", allow_duplicate=True),
        Input("erase-user-btn", "n_clicks"),
        State("user-table", "selected_rows"),
        State("user-table", "data"),
        State("active-role", "data"),
        prevent_initial_call=True
    )
    def handle_erase_user(n, selected_rows, data, active_role):
        from src.utils.rbac_utils import can_modify_data
        from dash import html
        if not n or not selected_rows or not data:
            return system.get_users_df().to_dict("records"), ""
        if not can_modify_data(active_role or "Harbourmaster"):
            return system.get_users_df().to_dict("records"), html.P(
                "Erase refused: active role is read-only.")
        uid = data[selected_rows[0]].get("user_id")
        system.erase_user_data(uid)
        return system.get_users_df().to_dict("records"), html.P(
            f"Erased personnel record {uid} (GDPR-style deletion).")
