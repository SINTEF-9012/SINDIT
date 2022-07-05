from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

from frontend.navbar import navbar_layout
from frontend.right_sidebar import right_sidebar_layout
from frontend.left_sidebar import left_sidebar_layout
from frontend.main_column import main_column_layout
from util.environment_and_configuration import ConfigGroups, get_configuration_int


def get_layout():
    """
    Main page layout
    :return:
    """
    return html.Div(
        children=[
            # Navbar:
            navbar_layout.get_layout(),
            # Body:
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            children=[
                                # Left sidebar (stats):
                                left_sidebar_layout.get_layout(),
                                # Main column (graph):
                                main_column_layout.get_layout(),
                                # Right sidebar (context details):
                                right_sidebar_layout.get_layout(),
                                # Interval pseudo component for periodic refreshes:
                                dcc.Interval(
                                    id="interval-component",
                                    interval=get_configuration_int(
                                        ConfigGroups.FRONTEND, "refresh_interval"
                                    ),
                                    # interval=cfg.config['frontend']['refresh_interval'],
                                    # interval=5000,
                                    n_intervals=0,
                                ),
                            ],
                            align="start",
                        ),
                    ]
                )
            ),
        ]
    )
