"""
SMPOOS Authentication Callbacks
Handles admin login, logout, and localStorage session management.
"""

from dash import Input, Output, State, html, callback_context, no_update
import dash_bootstrap_components as dbc
from src.utils.auth_utils import verify_admin_credentials, get_admin_info


def register_auth_callbacks(app, system):
    """
    Register authentication callbacks with the Dash app.

    Args:
        app: Dash application instance
        system: SMPOOS system instance
    """

    @app.callback(
        Output("authenticated-user", "data"),
        Output("login-error", "children"),
        Input("login-btn", "n_clicks"),
        [State("login-user-id", "value"),
         State("login-password", "value")],
        prevent_initial_call=True
    )
    def handle_login(n_clicks, username, password):
        """
        Handle admin login attempt.

        Args:
            n_clicks: Number of clicks on login button
            username: Entered username
            password: Entered password

        Returns:
            Tuple of (user_data, error_message)
        """
        if not username or not password:
            return None, html.Div([
                html.I(),
                "Please enter both Username and Password"
            ])

        # Verify admin credentials
        if verify_admin_credentials(username, password):
            # Get admin info and store in localStorage
            admin_info = get_admin_info()
            return admin_info, ""
        else:
            return None, html.Div([
                html.I(),
                "Invalid Username or Password. Please try again."
            ])

    @app.callback(
        Output("authenticated-user", "data", allow_duplicate=True),
        Input("logout-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def handle_logout(n_clicks):
        """
        Handle user logout - clears localStorage session.

        Args:
            n_clicks: Number of clicks on logout button

        Returns:
            None (clears session from localStorage)
        """
        if n_clicks and n_clicks > 0:
            return None
        return no_update

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Input("authenticated-user", "data"),
        prevent_initial_call=True
    )
    def redirect_on_logout(user_data):
        """
        Redirect to login page when user logs out.

        Args:
            user_data: User session data

        Returns:
            Pathname to redirect to (string)
        """
        # Check if this was triggered by logout (user_data changed to None)
        if callback_context.triggered:
            prop_id = callback_context.triggered[0]['prop_id']
            # Only redirect if authenticated-user changed to None
            if prop_id == 'authenticated-user.data' and user_data is None:
                return "/"
        return no_update
