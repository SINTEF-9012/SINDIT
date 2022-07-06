from dash import html, dcc
from datetime import datetime, date, timedelta
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import dash_daq as daq

# Use the following function when accessing the value of 'my-slider'
# in callbacks to transform the output value to logarithmic
def transform_value(value):

    return timedelta(milliseconds=(10**value))


def get_layout():
    return html.Div(
        id="datetime-selector-container",
        children=[
            html.Div("Select visualize date and time"),
            dbc.Row(
                children=[
                    daq.NumericInput(
                        id="datetime-selector-range-days",
                        label="Days",
                        min=0,
                        max=365,
                        value=0,
                        style={"width": 70},
                        persistence=True,
                        persistence_type="session",
                    ),
                    daq.NumericInput(
                        id="datetime-selector-range-hours",
                        label="Hours",
                        min=0,
                        max=24,
                        value=0,
                        style={"width": 70},
                        persistence=True,
                        persistence_type="session",
                    ),
                    daq.NumericInput(
                        id="datetime-selector-range-min",
                        label="Min.",
                        min=0,
                        max=60,
                        value=0,
                        style={"width": 70},
                        persistence=True,
                        persistence_type="session",
                    ),
                    daq.NumericInput(
                        id="datetime-selector-range-sec",
                        label="Sec.",
                        value=10.00,
                        min=0,
                        max=60,
                        style={"width": 65},
                        persistence=True,
                        persistence_type="session",
                    ),
                ]
            ),
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
                # value=datetime.now().date(),
                # style={"width": 250},
                # required=True,
                disabled=True,
                persistence=True,
                persistence_type="session",
            ),
            dmc.TimeInput(
                id="datetime-selector-time",
                label="Observed Time:",
                # description="Data visualized up to this time",
                # style={"width": 250},
                # error="Enter a valid time",
                withSeconds=True,
                # value=datetime.now(),
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
