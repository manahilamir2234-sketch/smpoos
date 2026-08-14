"""
Analytics page callbacks: date filtering and berth suggestions.
"""

from dash import Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px


def register_analytics_callbacks(app, system):
    """Register analytics-related Dash callbacks."""

    @app.callback(
        Output("analytics-charts-container", "children"),
        Input("date-filter", "start_date"),
        Input("date-filter", "end_date"),
        prevent_initial_call=True,
    )
    def filter_analytics_by_date(start_date, end_date):
        df_loc = system.get_locations_df()
        df_notif = system.get_notifications_df()

        if start_date and end_date and not df_notif.empty:
            dates = df_notif["timestamp"].astype(str).str[:10]
            df_notif = df_notif[
                (dates >= str(start_date)[:10]) & (dates <= str(end_date)[:10])
            ]

        capacity_by_type = df_loc.groupby("type")["capacity_tonnes"].sum().reset_index()
        fig_capacity = px.bar(
            capacity_by_type,
            x="type",
            y="capacity_tonnes",
            title="Capacity Utilization by Location Type",
            template="plotly_white",
            color="type",
        )
        fig_capacity.update_layout(showlegend=False)

        if df_notif.empty:
            fig_severity = px.pie(title="No alerts in selected range")
            fig_heat = px.scatter(title="No heatmap data")
            alert_fig = px.bar(title="No alert-type data")
        else:
            severity_counts = df_notif["severity"].value_counts().reset_index()
            severity_counts.columns = ["severity", "count"]
            fig_severity = px.pie(
                severity_counts,
                names="severity",
                values="count",
                title="Alert Severity Distribution",
                hole=0.4,
                template="plotly_white",
            )
            alert_counts = df_notif["alert_type"].value_counts().reset_index()
            alert_counts.columns = ["alert_type", "count"]
            alert_fig = px.bar(
                alert_counts,
                x="alert_type",
                y="count",
                title="Alerts by Type",
                template="plotly_white",
            )
            tmp = df_notif.copy()
            tmp["hour"] = tmp["timestamp"].astype(str).str[11:13]
            heat = tmp.groupby(["hour", "severity"]).size().reset_index(name="count")
            fig_heat = px.density_heatmap(
                heat,
                x="hour",
                y="severity",
                z="count",
                title="Alert Activity Heatmap (Hour vs Severity)",
                template="plotly_white",
            )

        suggestion = system.suggest_berth_allocation()

        row1 = dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                dcc.Graph(
                                    figure=px.pie(
                                        df_loc,
                                        names="type",
                                        hole=0.5,
                                        template="plotly_white",
                                        title="Asset Mix by Type",
                                    )
                                )
                            )
                        ]
                    ),
                    md=4,
                ),
                dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=alert_fig))]), md=4),
                dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=fig_severity))]), md=4),
            ],
            className="mb-3",
        )

        row2 = dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Port Infrastructure Load Analysis"),
                            dbc.CardBody(
                                dcc.Graph(
                                    figure=px.treemap(
                                        df_loc,
                                        path=["type", "status"],
                                        values="capacity_tonnes",
                                        template="plotly_white",
                                    )
                                )
                            ),
                        ]
                    ),
                    md=4,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Capacity Utilization by Location Type"),
                            dbc.CardBody(dcc.Graph(figure=fig_capacity)),
                        ]
                    ),
                    md=4,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Operational Congestion Heatmap"),
                            dbc.CardBody(dcc.Graph(figure=fig_heat)),
                        ]
                    ),
                    md=4,
                ),
            ]
        )

        return [
            row1,
            row2,
            dbc.Alert(
                suggestion, color="info", className="mt-3", id="berth-suggestion-text"
            ),
        ]
