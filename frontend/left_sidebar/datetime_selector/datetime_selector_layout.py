from dash import html
from datetime import datetime, date
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc


def get_layout():
    return html.Div(
        id="datetime-selector-container",
        children=[
            html.Div("Select visualize date and time"),
            dbc.Checkbox(
                id="realtime-switch-input",
                label="Show real-time data",
                value=True,
                persistence=True,
                persistence_type="session",
            ),
            dmc.DatePicker(
                id="datetime-selector-date",
                label="Observed Date",
                # description="Data visualized up to this date",
                value=datetime.now().date(),
                style={"width": 250},
                # required=True,
                disabled=True,
                persistence=True,
                persistence_type="session",
            ),
            dmc.TimeInput(
                id="datetime-selector-time",
                label="Observed Time:",
                # description="Data visualized up to this time",
                style={"width": 250},
                # error="Enter a valid time",
                withSeconds=True,
                value=datetime.now(),
                persistence=True,
                persistence_type="session",
                disabled=True,
            ),
        ],
    )


def get_content():
    return html.Div("Will contain connection status etc...")
    # TODO: connection status, time, node count, edge count...
    # Directly load from the API as this will be reloaded frequently
