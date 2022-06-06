from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import requests

import helper_functions
from app import app
import environment.settings as stngs
from frontend import frontend_helpers

API_URI = stngs.FAST_API_URI


def get_layout():
    cygraph = requests.get(API_URI + '/get_factory_cytoscape_from_neo4j').json()
    cystyle = helper_functions._load_json(app.get_asset_url('cy-style.json'))

    return dbc.Col(
        children=[
            frontend_helpers._draw_graph(cygraph, cystyle),
            html.Div(
                children=[dcc.Input(id='input-on-submit', type='number', value=40), 'Simulation duration']),
            html.Button('Simulate', id='submit-val', n_clicks=0),
            html.Button('Reset', id='reset-val', n_clicks=0),
            html.Div(id='run_event_sim_button', children='Enter a simulation duration'),
        ],
        width=8
    )

