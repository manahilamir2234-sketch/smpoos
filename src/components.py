from dash import html, dcc
import dash_bootstrap_components as dbc


def create_sidebar():
    """
    Create the sidebar navigation with role selector and nav links.

    Returns:
        html.Div: Sidebar component with navigation and role selector.
    """
    return html.Div(
        [
            # Branding Section
            html.Div([
                html.H2("SMPOOS"),
                html.P("CONTROL CENTER"),
            ]),

            html.Hr(),

            # Role Selector
            html.Div([
                html.Label("Active Role:"),
                dbc.Select(
                    id="role-selector",
                    options=[
                        {"label": "Harbourmaster", "value": "Harbourmaster"},
                        {"label": "Administrator", "value": "Administrator"},
                        {"label": "Operations Supervisor",
                            "value": "Operations Supervisor"},
                        {"label": "Safety Officer", "value": "Safety Officer"},
                        {"label": "Crane Operator", "value": "Crane Operator"},
                        {"label": "Stevedore", "value": "Stevedore"},
                    ],
                    value="Harbourmaster",
                )
            ]),

            html.Hr(),

            # Nav Menu
            dbc.Nav(
                [
                    dbc.NavLink("Dashboard", href="/", active="exact"),
                    html.Br(),
                    dbc.NavLink("Asset Registry", href="/assets", active="exact"),
                    html.Br(),
                    dbc.NavLink("Strategic Analytics", href="/analytics", active="exact"),
                    html.Br(),
                    dbc.NavLink("Routes", href="/routes", active="exact"),
                    html.Br(),
                    dbc.NavLink("Personnel", href="/users", active="exact"),
                    html.Br(),
                    dbc.NavLink("Notifications", href="/notifications", active="exact"),
                ],
                vertical=True,
            ),

            # Bottom Status
            html.Div([
                html.Div([
                    html.Span(),
                    html.Small("Vessel Tracking: ACTIVE (simulated)")
                ]),
                html.Small("System Health: 100%"),
                html.Hr(),
                html.Small(id="rbac-status-text", children="Active role: Harbourmaster"),
                html.Br(),
                dbc.Button("Logout", id="logout-btn", color="secondary", size="sm", className="mt-2"),
            ])
        ],
    )


def create_crud_modal(entity_name, modal_id, fields, submit_button_id, title_prefix="Add"):
    """
    Create a reusable CRUD modal with form inputs.

    Args:
        entity_name (str): Name of the entity (e.g., "Route", "User").
        modal_id (str): ID for the modal component.
        fields (list): List of field dictionaries with keys:
            - id (str): Input component ID
            - label (str): Label text for the field
            - type (str): Input type - "text", "number", "dropdown", "textarea"
            - options (list, optional), "value": str} for dropdowns
            - placeholder (str, optional): Placeholder text
            - row (bool, optional): If True, place in same row as previous field
        submit_button_id (str): ID for the submit button.
        title_prefix (str): Prefix for modal title (e.g., "Add", "Edit").

    Returns:
        dbc.Modal: Configured modal component with form fields.
    """
    form_rows = []
    current_row = []

    for field in fields:
        field_type = field.get("type", "text")
        field_id = field.get("id")
        label = field.get("label", "")
        placeholder = field.get("placeholder", "")
        options = field.get("options", [])
        row = field.get("row", False)

        # Create the input component based on type
        if field_type == "dropdown":
            input_component = dbc.Select(
                id=field_id,
                options=options,
                placeholder=placeholder
            )
        elif field_type == "textarea":
            input_component = dbc.Textarea(
                id=field_id,
                placeholder=placeholder,
                rows=3
            )
        elif field_type == "number":
            input_component = dbc.Input(
                id=field_id,
                type="number",
                placeholder=placeholder
            )
        else:  # default to text
            input_component = dbc.Input(
                id=field_id,
                type="text",
                placeholder=placeholder
            )

        field_wrapper = html.Div([
            dbc.Label(label),
            input_component
        ])

        if row and current_row:
            # Add to current row
            current_row.append(dbc.Col(field_wrapper, width=6))
        else:
            # Flush any existing row
            if current_row:
                form_rows.append(dbc.Row(current_row))
                current_row = []
            # Start new field (either full width or start of row)
            if row:
                current_row = [dbc.Col(field_wrapper, width=6)]
            else:
                form_rows.append(field_wrapper)

    # Flush remaining row fields
    if current_row:
        form_rows.append(dbc.Row(current_row))

    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(
            f"{title_prefix} {entity_name}"), close_button=True),
        dbc.ModalBody(form_rows),
        dbc.ModalFooter(
            dbc.Button(
                f"{title_prefix} {entity_name}",
                id=submit_button_id,
                color="success"
            )
        )
    ], id=modal_id, is_open=False)


def stat_card(title, value, icon, color, stat_id=None):
    # Only include id if stat_id is provided
    h3_props = {}
    if stat_id is not None:
        h3_props["id"] = stat_id
    
    card_content = dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6(title),
                    html.H3(value, **h3_props)
                ]),
            ])
        ])
    ])
    return card_content


def section_header(title, subtitle=None):
    return html.Div([
        html.H2(title),
        html.P(subtitle) if subtitle else None,
        html.Hr()
    ])
