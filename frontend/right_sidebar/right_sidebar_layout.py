import dash_bootstrap_components as dbc
from dash import dcc
from dash import html


def get_layout():
    """
    Layout of the right sidebar. Contains context details for selected elements of the main graph
    :return:
    """
    return dbc.Col(
        children=[
            dcc.Tabs(id='tabs-infos', value='tab-nodes', children=[
                dcc.Tab(label='Node information', value='tab-nodes'),
                # dcc.Tab(label='Parts history', value='tab-parts'),
                dcc.Tab(label='Sensors time-series', value='tab-sensors') # TODO: make tab for node data instead
            ]),
            html.Div(id='tabs-content')
        ],
        width=3
    )

