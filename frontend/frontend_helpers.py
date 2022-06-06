import dash
import dash_cytoscape as cyto
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import requests
import json
import datetime
import plotly
import pandas as pd
import numpy as np
import environment.settings as stngs
import random

GRAPH_CARD_STYLE = {}  # {'background-image': ['url('+BACKGROUND_IMAGE+')'],

def _draw_graph(cygraph, cystyle):
    return html.Div([
        dbc.Card([
            dbc.CardHeader("Factory graph"),
            dbc.CardBody([
                cyto.Cytoscape(
                    id='cytoscape-graph',
                    layout={'name': 'preset'},
                    style={'width': '100%', 'height': '770px'},
                    stylesheet=cystyle,
                    elements=cygraph)
            ], style=GRAPH_CARD_STYLE)
        ]),
    ])


# Layout
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}


