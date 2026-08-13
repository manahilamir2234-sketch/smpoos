from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
from .components import stat_card, section_header, create_crud_modal

TABLE_STYLE = {}


def get_login_layout():
    """
    Create the login page layout with username/password form.

    Returns:
        html.Div: Login page layout component
    """
    return html.Div([
        html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H2("SMPOOS"),
                        html.P("CONTROL CENTER"),
                    ]),

                    dbc.Form([
                        dbc.Row([
                            dbc.Label("Username"),
                            dbc.Input(
                                id="login-user-id",
                                placeholder="Enter admin username",
                                type="text",
                            )
                        ]),
                        dbc.Row([
                            dbc.Label("Password"),
                            dbc.Input(
                                id="login-password",
                                placeholder="Enter your password",
                                type="password",
                            )
                        ]),

                        html.Div(
                            id="login-error",
                            children="",
                        ),

                        dbc.Button(
                            ["Login"],
                            id="login-btn",
                            color="info"
                        ),

                        html.Div([
                            html.Hr(),
                            html.P([
                                html.Span("Default credentials: "),
                                html.Code("admin / admin123")
                            ])
                        ])
                    ])
                ])
            ])
        ])
    ])


def get_overview_layout(df_loc, df_route, df_notif):
    """
    Create the Dashboard/Overview page layout.

    Args:
        df_loc (DataFrame): Locations data
        df_route (DataFrame): Routes data
        df_notif (DataFrame): Notifications data

    Returns:
        html.Div: Dashboard layout component
    """
    # Executive Metrics
    metrics = html.Table([
        html.Tr([
            html.Td(stat_card("Berth Occupancy", f"{len(df_loc[df_loc['status'] == 'Active'])}/{len(df_loc)}", "", "green", "stat-berth-occupancy")),
            html.Td(stat_card("Active Routes", len(df_route[df_route['status'] == 'Open']), "", "blue", "stat-active-routes")),
            html.Td(stat_card("Critical Alerts", len(df_notif[df_notif['severity'] == 'Critical']), "", "red", "stat-critical-alerts")),
            html.Td(stat_card("Incoming Vessels", "12", "", "orange"))
        ])
    ])

    # Layer 2: Main Analytical Chart (Hero Section)
    fig_route = px.strip(
        df_route,
        x='distance_km',
        y='route_type',
        color='status',
        color_discrete_map={"Open": "#27ae60",
                            "Restricted": "#f39c12", "Closed": "#e74c3c"},
        labels={
            'distance_km': 'Transit Distance (KM)', 'route_type': 'Vessel Network Category', 'status': 'Logistics Status'},
        template="plotly_white"
    )

    fig_route.update_traces(marker=dict(
        size=12, opacity=0.6, line=dict(width=1, color='white')))

    fig_route.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=True, zeroline=False),
        yaxis=dict(showgrid=True)
    )

    # Prepare notification data with acknowledge buttons
    notif_data = df_notif.sort_values(
        'timestamp', ascending=False).head(10).to_dict('records')
    notif_columns = [{"name": i.title().replace("_", " "), "id": i}
                     for i in ['timestamp', 'alert_type', 'severity', 'message']]

    return html.Div([
        section_header("Operational Command Deck",
                       "Strategic real-time HarbourView maritime logistics overview"),
        metrics,

        # HERO SECTION: The Graph (Now Full Width for Clarity)
        dbc.Card([
            dbc.CardHeader([html.I(),
                           "Transit Network Load Analysis"]),
            dbc.CardBody(dcc.Graph(figure=fig_route, config={
                         'responsive': True}))
        ]),

        # Layer 3: Secondary Information (Operational Log)
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader([
                    html.I(),
                    "Recent High-Priority Alert Feed"
                ]),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='overview-alert-table',
                        data=notif_data,
                        columns=notif_columns,
                        sort_action="native",
                        filter_action="native",
                        page_size=10,
                        row_selectable="single",
                        selected_rows=[]
                    ),
                    html.Div([
                        dbc.Button(
                            [html.I(),
                             "Acknowledge Selected"],
                            id="acknowledge-alert-btn",
                            color="success",
                            size="sm",
                            disabled=True
                        )
                    ])
                ])
            ]), width=12),
        ]),

        # Audit Log Section
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader([
                    html.I(),
                    "Recent Audit Log"
                ]),
                dbc.CardBody(
                    html.Div(
                        id="audit-log-section",
                        children=[
                            html.P("Loading audit entries...")
                        ]
                    )
                )
            ]), width=12)
        ])
    ])


def get_asset_layout(df_loc):
    """
    Create the Asset Registry page layout with CRUD operations.

    Args:
        df_loc (DataFrame): Locations data

    Returns:
        html.Div: Asset registry layout component
    """
    return html.Div([
        section_header("Asset Registry",
                       "Infrastructure management and resource allocation"),

        # Hidden store for selected location ID
        dcc.Store(id="selected-loc-id"),

        dbc.Row([
            dbc.Col(dbc.Button([html.I(), "Register New Asset"],
                    id="open-modal-btn", color="primary"), width="auto"),
            dbc.Col(dbc.Input(id="asset-search", placeholder="Search assets..."), width=4)
        ]),

        # Action buttons row (Edit/Delete)
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button([html.I(), "Edit Selected"],
                               id="edit-loc-btn", color="warning", outline=True, disabled=True),
                    dbc.Button([html.I(), "Delete Selected"],
                               id="delete-loc-btn", color="danger", outline=True, disabled=True),
                ])
            ], width="auto")
        ]),

        dbc.Card([
            dbc.CardBody(dash_table.DataTable(
                id='asset-table',
                data=df_loc.to_dict('records'),
                columns=[{"name": i.title().replace("_", " "), "id": i}
                         for i in df_loc.columns],
                page_size=15,
                filter_action="native",
                sort_action="native",
                row_selectable="single",
                selected_rows=[]
            ))
        ]),

        # Add Location Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(
                "New Port Asset Registration"), close_button=True),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([dbc.Label("Asset ID"), dbc.Input(
                        id="new-loc-id", placeholder="L0XXX")]),
                    dbc.Col([dbc.Label("Capacity"), dbc.Input(
                        id="new-loc-capacity", type="number")]),
                ]),
                dbc.Label("Common Name"), dbc.Input(id="new-loc-name",
                                                    placeholder="e.g. Berth 12"),
                dbc.Label("Asset Type"),
                dbc.Select(id="new-loc-type", options=[
                    {"label": "Berth", "value": "Berth"},
                    {"label": "Storage Yard", "value": "Storage Yard"},
                    {"label": "Fuel Dock", "value": "Fuel Dock"},
                    {"label": "Customs Zone", "value": "Customs Zone"},
                    {"label": "Maintenance Area", "value": "Maintenance Area"}
                ]),
                dbc.Label("Status"),
                dbc.Select(id="new-loc-status", options=[
                    {"label": "Active", "value": "Active"},
                    {"label": "Inactive", "value": "Inactive"},
                    {"label": "Under Maintenance", "value": "Under Maintenance"}
                ]),
            ]),
            dbc.ModalFooter(dbc.Button("Commit Registration", id="submit-new-loc",
                            color="success"))
        ], id="add-loc-modal", is_open=False),

        # Edit Location Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(
                "Edit Port Asset"), close_button=True),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([dbc.Label("Asset ID"), dbc.Input(
                        id="edit-loc-id", disabled=True)]),
                    dbc.Col([dbc.Label("Capacity (tonnes)"), dbc.Input(
                        id="edit-loc-capacity", type="number")]),
                ]),
                dbc.Label("Common Name"), dbc.Input(
                    id="edit-loc-name"),
                dbc.Label("Asset Type"),
                dbc.Select(id="edit-loc-type", options=[
                    {"label": "Berth", "value": "Berth"},
                    {"label": "Storage Yard", "value": "Storage Yard"},
                    {"label": "Fuel Dock", "value": "Fuel Dock"},
                    {"label": "Customs Zone", "value": "Customs Zone"},
                    {"label": "Maintenance Area", "value": "Maintenance Area"}
                ]),
                dbc.Label("Status"),
                dbc.Select(id="edit-loc-status", options=[
                    {"label": "Active", "value": "Active"},
                    {"label": "Inactive", "value": "Inactive"},
                    {"label": "Under Maintenance", "value": "Under Maintenance"}
                ]),
            ]),
            dbc.ModalFooter(dbc.Button("Update Asset", id="submit-edit-loc",
                            color="warning"))
        ], id="edit-loc-modal", is_open=False),

        # Delete Confirmation Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(
                "Confirm Deletion"), close_button=True),
            dbc.ModalBody([
                html.P("Are you sure you want to delete this location?"),
                html.P("This action cannot be undone.")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-delete-loc",
                           color="secondary"),
                dbc.Button("Delete", id="confirm-delete-loc",
                           color="danger")
            ])
        ], id="delete-loc-modal", is_open=False)
    ])


def get_analytics_layout(df_loc, df_notif):
    """
    Create the Analytics page layout with charts and filters.

    Args:
        df_loc (DataFrame): Locations data
        df_notif (DataFrame): Notifications data

    Returns:
        html.Div: Analytics layout component
    """
    # Capacity utilization by location type
    capacity_by_type = df_loc.groupby(
        'type')['capacity_tonnes'].sum().reset_index()
    fig_capacity = px.bar(
        capacity_by_type,
        x='type',
        y='capacity_tonnes',
        title='Capacity Utilization by Location Type',
        labels={
            'capacity_tonnes': 'Total Capacity (tonnes)', 'type': 'Location Type'},
        template="plotly_white",
        color='type'
    )
    fig_capacity.update_layout(
        showlegend=False, margin=dict(l=20, r=20, t=50, b=20))

    # Severity distribution pie chart
    severity_counts = df_notif['severity'].value_counts().reset_index()
    severity_counts.columns = ['severity', 'count']
    fig_severity = px.pie(
        severity_counts,
        names='severity',
        values='count',
        title='Alert Severity Distribution',
        hole=0.4,
        template="plotly_white",
        color='severity',
        color_discrete_map={
            'Critical': '#e74c3c',
            'High': '#f39c12',
            'Medium': '#3498db',
            'Low': '#27ae60'
        }
    )
    fig_severity.update_layout(margin=dict(l=20, r=20, t=50, b=20))

    # Charts Row 1 — Bootstrap grid (assessment brief recommends DBC grids)
    charts_row_1 = dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(
            figure=px.pie(df_loc, names='type', hole=0.5, template="plotly_white",
                          title="Asset Mix by Type")))]), md=4),
        dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(
            figure=px.bar(df_notif['alert_type'].value_counts().reset_index(),
                          x='alert_type', y='count', template="plotly_white",
                          title="Alerts by Type")))]), md=4),
        dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=fig_severity))]), md=4),
    ], className="mb-3")

    # Congestion-style heatmap of alert activity by hour (analytics requirement)
    try:
        notif_copy = df_notif.copy()
        notif_copy['hour'] = notif_copy['timestamp'].astype(str).str[11:13]
        heat = notif_copy.groupby(['hour', 'severity']).size().reset_index(name='count')
        fig_heat = px.density_heatmap(
            heat, x='hour', y='severity', z='count',
            title='Alert Activity Heatmap (Hour vs Severity)',
            template='plotly_white'
        )
    except Exception:
        fig_heat = px.scatter(title='Alert heatmap unavailable')

    charts_row_2 = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Port Infrastructure Load Analysis"),
            dbc.CardBody(dcc.Graph(figure=px.treemap(
                df_loc, path=['type', 'status'], values='capacity_tonnes',
                template="plotly_white")))
        ]), md=4),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Capacity Utilization by Location Type"),
            dbc.CardBody(dcc.Graph(figure=fig_capacity))
        ]), md=4),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Operational Congestion Heatmap"),
            dbc.CardBody(dcc.Graph(figure=fig_heat))
        ]), md=4),
    ])

    return html.Div([
        section_header("Strategic Analytics",
                       "Performance assessment and historical trends"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col(dbc.Label("Date Range Filter"), width="auto"),
                            dbc.Col(dcc.DatePickerRange(
                                id='date-filter',
                                start_date_placeholder_text='Start Date',
                                end_date_placeholder_text='End Date'
                            ))
                        ])
                    ])
                ])
            ], width=12)
        ], className="mb-3"),
        charts_row_1,
        charts_row_2
    ])


def get_route_layout(df_routes):
    """
    Create the Route Management page layout.

    Args:
        df_routes (DataFrame): Routes data

    Returns:
        html.Div: Route management layout component
    """
    # Route type options
    route_type_options = [
        {"label": "Shipping Lane", "value": "Shipping Lane"},
        {"label": "Tugboat Transit Path", "value": "Tugboat Transit Path"},
        {"label": "Automated Guided Vehicle Route",
            "value": "Automated Guided Vehicle Route"},
        {"label": "Truck Path", "value": "Truck Path"}
    ]

    # Status options
    status_options = [
        {"label": "Open", "value": "Open"},
        {"label": "Restricted", "value": "Restricted"},
        {"label": "Closed", "value": "Closed"}
    ]

    return html.Div([
        section_header("Route Management",
                       "Logistics route planning and status monitoring"),

        # Hidden store for selected route ID
        dcc.Store(id="selected-route-id"),

        dbc.Row([
            dbc.Col(dbc.Button([html.I(), "Add Route"],
                    id="open-route-modal-btn", color="primary"), width="auto"),
        ]),

        # Action buttons row (Edit/Delete)
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button([html.I(), "Edit Selected"],
                               id="edit-route-btn", color="warning", outline=True, disabled=True),
                    dbc.Button([html.I(), "Delete Selected"],
                               id="delete-route-btn", color="danger", outline=True, disabled=True),
                ])
            ], width="auto")
        ]),

        dbc.Card([
            dbc.CardBody(dash_table.DataTable(
                id='route-table',
                data=df_routes.to_dict('records'),
                columns=[{"name": i.title().replace("_", " "), "id": i} for i in [
                    'route_id', 'start_location', 'end_location', 'route_type', 'distance_km', 'status']],
                page_size=15,
                filter_action="native",
                sort_action="native",
                row_selectable="single",
                selected_rows=[]
            ))
        ]),

        # Add Route Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(
                "Add New Route"), close_button=True),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([dbc.Label("Route ID"), dbc.Input(
                        id="new-route-id", placeholder="R0XXX")]),
                    dbc.Col([dbc.Label("Distance (km)"), dbc.Input(
                        id="new-route-distance", type="number", placeholder="0.00")]),
                ]),
                dbc.Row([
                    dbc.Col([dbc.Label("Start Location"), dbc.Input(
                        id="new-route-start", placeholder="L0XXX")]),
                    dbc.Col([dbc.Label("End Location"), dbc.Input(
                        id="new-route-end", placeholder="L0XXX")]),
                ]),
                dbc.Label("Route Type"),
                dbc.Select(id="new-route-type",
                           options=route_type_options),
                dbc.Label("Status"),
                dbc.Select(id="new-route-status",
                           options=status_options),
            ]),
            dbc.ModalFooter(dbc.Button("Add Route", id="submit-new-route",
                            color="success"))
        ], id="add-route-modal", is_open=False),

        # Edit Route Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Edit Route"), close_button=True),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([dbc.Label("Route ID"), dbc.Input(
                        id="edit-route-id", disabled=True)]),
                    dbc.Col([dbc.Label("Distance (km)"), dbc.Input(
                        id="edit-route-distance", type="number")]),
                ]),
                dbc.Row([
                    dbc.Col([dbc.Label("Start Location"),
                            dbc.Input(id="edit-route-start")]),
                    dbc.Col([dbc.Label("End Location"),
                            dbc.Input(id="edit-route-end")]),
                ]),
                dbc.Label("Route Type"),
                dbc.Select(id="edit-route-type",
                           options=route_type_options),
                dbc.Label("Status"),
                dbc.Select(id="edit-route-status",
                           options=status_options),
            ]),
            dbc.ModalFooter(dbc.Button("Update Route", id="submit-edit-route",
                            color="warning"))
        ], id="edit-route-modal", is_open=False),

        # Delete Confirmation Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(
                "Confirm Deletion"), close_button=True),
            dbc.ModalBody([
                html.P("Are you sure you want to delete this route?"),
                html.P("This action cannot be undone.")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-delete-route",
                           color="secondary"),
                dbc.Button("Delete", id="confirm-delete-route",
                           color="danger")
            ])
        ], id="delete-route-modal", is_open=False)
    ])


def get_user_layout(df_users):
    """
    Create the User/Personnel Management page layout.

    Args:
        df_users (DataFrame): Users data

    Returns:
        html.Div: User management layout component
    """
    # Role options
    role_options = [
        {"label": "Harbourmaster", "value": "Harbourmaster"},
        {"label": "Administrator", "value": "Administrator"},
        {"label": "Crane Operator", "value": "Crane Operator"},
        {"label": "Maintenance Engineer", "value": "Maintenance Engineer"},
        {"label": "Security Officer", "value": "Security Officer"},
        {"label": "Stevedore", "value": "Stevedore"},
        {"label": "Logistics Coordinator", "value": "Logistics Coordinator"},
        {"label": "Operations Supervisor", "value": "Operations Supervisor"},
        {"label": "Safety Officer", "value": "Safety Officer"}
    ]

    # Active options
    active_options = [
        {"label": "Yes", "value": "Yes"},
        {"label": "No", "value": "No"}
    ]

    return html.Div([
        section_header("Personnel Management",
                       "User account administration and role assignments"),

        # Hidden store for selected user ID
        dcc.Store(id="selected-user-id"),

        dbc.Row([
            dbc.Col(dbc.Button([html.I(), "Add User"],
                    id="open-user-modal-btn", color="primary"), width="auto"),
        ]),

        # Action buttons row (Edit/Delete)
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button([html.I(), "Edit Selected"],
                               id="edit-user-btn", color="warning", outline=True, disabled=True),
                    dbc.Button([html.I(), "Delete Selected"],
                               id="delete-user-btn", color="danger", outline=True, disabled=True),
                ])
            ], width="auto")
        ]),

        dbc.Card([
            dbc.CardBody(dash_table.DataTable(
                id='user-table',
                data=df_users.to_dict('records'),
                columns=[{"name": i.title().replace("_", " "), "id": i}
                         for i in ['user_id', 'name', 'role', 'email', 'active']],
                page_size=15,
                filter_action="native",
                sort_action="native",
                row_selectable="single",
                selected_rows=[]
            ))
        ]),

        # Add User Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Add New User"), close_button=True),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([dbc.Label("User ID"), dbc.Input(
                        id="new-user-id", placeholder="U0XXX")]),
                    dbc.Col([dbc.Label("Name"), dbc.Input(
                        id="new-user-name", placeholder="Full Name")]),
                ]),
                dbc.Label("Email"),
                dbc.Input(id="new-user-email", type="email",
                          placeholder="user@portauthority.com"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Role"),
                        dbc.Select(id="new-user-role", options=role_options)
                    ]),
                    dbc.Col([
                        dbc.Label("Active"),
                        dbc.Select(id="new-user-active",
                                   options=active_options)
                    ])
                ]),
            ]),
            dbc.ModalFooter(dbc.Button("Add User", id="submit-new-user",
                            color="success"))
        ], id="add-user-modal", is_open=False),

        # Edit User Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Edit User"), close_button=True),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([dbc.Label("User ID"), dbc.Input(
                        id="edit-user-id", disabled=True)]),
                    dbc.Col([dbc.Label("Name"), dbc.Input(id="edit-user-name")]),
                ]),
                dbc.Label("Email"),
                dbc.Input(id="edit-user-email",
                          type="email"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Role"),
                        dbc.Select(id="edit-user-role", options=role_options)
                    ]),
                    dbc.Col([
                        dbc.Label("Active"),
                        dbc.Select(id="edit-user-active",
                                   options=active_options)
                    ])
                ]),
            ]),
            dbc.ModalFooter(dbc.Button("Update User", id="submit-edit-user",
                            color="warning"))
        ], id="edit-user-modal", is_open=False),

        # Delete Confirmation Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(
                "Confirm Deletion"), close_button=True),
            dbc.ModalBody([
                html.P("Are you sure you want to delete this user?"),
                html.P("This action cannot be undone.")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-delete-user",
                           color="secondary"),
                dbc.Button("Delete", id="confirm-delete-user",
                           color="danger")
            ])
        ], id="delete-user-modal", is_open=False)
    ])


def get_notification_layout(df_notif):
    """
    Create the Notification Management page layout.

    Args:
        df_notif (DataFrame): Notifications data

    Returns:
        html.Div: Notification management layout component
    """
    # Alert type options
    alert_type_options = [
        {"label": "Equipment Failure", "value": "Equipment Failure"},
        {"label": "Hazardous Cargo Warning", "value": "Hazardous Cargo Warning"},
        {"label": "Security Notice", "value": "Security Notice"},
        {"label": "Weather Warning", "value": "Weather Warning"},
        {"label": "Berth Closure", "value": "Berth Closure"},
        {"label": "Congestion Alert", "value": "Congestion Alert"}
    ]

    # Severity options
    severity_options = [
        {"label": "Critical", "value": "Critical"},
        {"label": "High", "value": "High"},
        {"label": "Medium", "value": "Medium"},
        {"label": "Low", "value": "Low"}
    ]

    return html.Div([
        section_header("Notification Centre",
                       "Alert management and incident tracking"),

        # Hidden store for selected notification ID
        dcc.Store(id="selected-notif-id"),

        dbc.Row([
            dbc.Col([
                dbc.Button([html.I(), "Create Alert"],
                           id="open-notif-modal-btn", color="primary")
            ], width="auto"),
            dbc.Col([
                dbc.InputGroup([
                    dbc.InputGroupText(html.I()),
                    dbc.Select(
                        id="notif-severity-filter",
                        options=[{"label": "All Severities",
                                  "value": "all"}] + severity_options,
                        value="all",
                        placeholder="Filter by Severity"
                    )
                ])
            ], width=3)
        ]),

        # Action buttons row (Delete/Acknowledge)
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button([html.I(), "Acknowledge"],
                               id="acknowledge-notif-btn", color="success", outline=True, disabled=True),
                    dbc.Button([html.I(), "Delete"],
                               id="delete-notif-btn", color="danger", outline=True, disabled=True),
                ])
            ], width="auto")
        ]),

        dbc.Card([
            dbc.CardBody(dash_table.DataTable(
                id='notif-table',
                data=df_notif.to_dict('records'),
                columns=[{"name": i.title().replace("_", " "), "id": i} for i in [
                    'notification_id', 'alert_type', 'location_id', 'severity', 'message', 'timestamp']],
                page_size=15,
                filter_action="native",
                sort_action="native",
                row_selectable="single",
                selected_rows=[]
            ))
        ]),

        # Create Alert Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(
                "Create New Alert"), close_button=True),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([dbc.Label("Notification ID"), dbc.Input(
                        id="new-notif-id", placeholder="N0XXX")]),
                    dbc.Col([dbc.Label("Location ID"), dbc.Input(
                        id="new-notif-location", placeholder="L0XXX")]),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Alert Type"),
                        dbc.Select(id="new-notif-type",
                                   options=alert_type_options)
                    ]),
                    dbc.Col([
                        dbc.Label("Severity"),
                        dbc.Select(id="new-notif-severity",
                                   options=severity_options)
                    ])
                ]),
                dbc.Label("Message"),
                dbc.Textarea(
                    id="new-notif-message", placeholder="Enter alert message...", rows=3),
            ]),
            dbc.ModalFooter(dbc.Button("Create Alert", id="submit-new-notif",
                            color="success"))
        ], id="add-notif-modal", is_open=False),

        # Delete Confirmation Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(
                "Confirm Deletion"), close_button=True),
            dbc.ModalBody([
                html.P("Are you sure you want to delete this notification?"),
                html.P("This action cannot be undone.")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-delete-notif",
                           color="secondary"),
                dbc.Button("Delete", id="confirm-delete-notif",
                           color="danger")
            ])
        ], id="delete-notif-modal", is_open=False)
    ])
