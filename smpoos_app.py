import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import os

# Internal Imports
from src.components import create_sidebar
from src.layouts import (
    get_login_layout,
    get_overview_layout,
    get_asset_layout,
    get_analytics_layout,
    get_route_layout,
    get_user_layout,
    get_notification_layout
)
from src.smpoos_logic import SMPOOS
from src.callbacks import register_all_callbacks

# --- App Init ---
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}]
)
app.title = "SMPOOS Control Center"

# --- Data Handler ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
system = SMPOOS(data_dir=DATA_DIR)

# --- Master Layout ---
app.layout = html.Div([
    dcc.Location(id="url"),
    dcc.Store(id="authenticated-user", data=None),
    dcc.Interval(
        id="realtime-interval",
        interval=5000,
        n_intervals=0,
        max_intervals=-1
    ),
    html.Div(id="login-page"),
    
    html.Table([
        html.Tr([
            # Column 1: Sidebar
            html.Td(
                html.Div(create_sidebar(), id="sidebar-container")
            ),
            # Column 2: Content
            html.Td(
                html.Div(id="page-content")
            )
        ])
    ])
])




@app.callback(
    [Output("page-content", "children"),
     Output("sidebar-container", "style"),
     Output("page-content", "style")],
    [Input("url", "pathname"),
     Input("authenticated-user", "data")]
)
def route_handler(path, user_data):
    """
    Handle page routing based on URL pathname and authentication state.

    Args:
        path: The URL pathname
        user_data: Authenticated user data (None if not logged in)

    Returns:
        Tuple of (page_content, sidebar_style, content_style)
    """
    # If not authenticated, show login page and hide sidebar
    if user_data is None:
        # Return login layout and hide sidebar
        return get_login_layout(), {"display": "none"}, {}

    # User is authenticated, show sidebar
    sidebar_style = {"display": "block"}
    content_style = {}

    # Route to appropriate page
    if path == "/assets":
        return get_asset_layout(system.get_locations_df()), sidebar_style, content_style
    if path == "/analytics":
        return get_analytics_layout(system.get_locations_df(), system.get_notifications_df()), sidebar_style, content_style
    if path == "/routes":
        return get_route_layout(system.get_routes_df()), sidebar_style, content_style
    if path == "/users":
        return get_user_layout(system.get_users_df()), sidebar_style, content_style
    if path == "/notifications":
        return get_notification_layout(system.get_notifications_df()), sidebar_style, content_style

    # Default: Dashboard/Overview
    return get_overview_layout(
        system.get_locations_df(),
        system.get_routes_df(),
        system.get_notifications_df()
    ), sidebar_style, content_style




# This registers all CRUD, authentication, and real-time callbacks
register_all_callbacks(app, system)




if __name__ == "__main__":
    print("=" * 60)
    print("SMPOOS Control Center - Smart Maritime Port Operations")
    print("=" * 60)
    print("\nApplication starting...")
    print("Admin login credentials:")
    print("  - Username: admin")
    print("  - Password: admin123")
    print("\n(Note: Credentials can be changed in .env file)")
    print("=" * 60)
    app.run(debug=True, port=8050)
