import dash_cytoscape as cyto
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import requests
import json
import datetime
import pandas as pd
import numpy as np
import environment.environment as stngs
import random

from frontend import api_client

# TODO: refactor away


def _draw_table_part_infos(data):
    header_style = {'color': 'black', 'fontSize': 14, 'font-weight': 'bold'}
    rows = []
    if data:
        rows.append(html.Tr([html.Td(data['data']['type'], style=header_style), html.Td(data['data']['id'])]))
        rows.append(html.Tr([html.Td('Description:'), html.Td(data['data']['label'])]))

    table_body = [html.Tbody(rows)]
    table = dbc.Table(table_body, id='part_node_info-text', bordered=False)

    return table







def _draw_parts_graph(parts_cygraph, cystyle):
    cyto_card_graph = cyto.Cytoscape(
        id='cytoscape-parts-graph',
        layout={'name': 'cose'},
        style={'width': '100%', 'height': '200px'},
        stylesheet=cystyle,
        elements=parts_cygraph)

    return html.Div([
        dbc.Card([
            dbc.CardHeader("Parts graph"),
            dbc.CardBody([cyto_card_graph]),
        ]),
    ])




