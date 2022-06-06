from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

import global_config as cfg
from frontend.navbar import navbar
from frontend.right_sidebar import right_sidebar
from frontend.left_sidebar import left_sidebar
from frontend.main_column import main_column


def get_layout():
    """
    Main page layout
    :return:
    """
    return html.Div(
        children=[
            # Navbar:
            navbar.get_layout(),
            # Body:
            dbc.Card(
                dbc.CardBody([
                    dbc.Row(
                        children=[
                            # Left sidebar (stats):
                            left_sidebar.get_layout(),
                            # Main column (graph):
                            main_column.get_layout(),
                            # Right sidebar (context details):
                            right_sidebar.get_layout(),

                            # Interval pseudo component for periodic refreshes:
                            dcc.Interval(
                                id='interval-component',
                                interval=cfg.config['frontend']['refresh_interval'],
                                n_intervals=0)
                        ],
                        align='start'
                    ),
                ])
            )
        ])
