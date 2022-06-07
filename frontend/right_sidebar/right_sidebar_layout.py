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
            dcc.Tabs(id='tabs-infos', value='tab-node-information', children=[
                dcc.Tab(label='Node information', value='tab-node-information'),
                dcc.Tab(label='Node data', value='tab-node-data')
            ]),
            html.Div(id='tabs-content')
        ],
        width=3
    )

