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


def _draw_table_node_infos(data):
    header_style = {'color': 'black', 'fontSize': 14, 'font-weight': 'bold'}
    rows = []
    if data:
        print(data['data']['id'] + ': ' + str(data['position']['x']) + '/' + str(data['position']['y']))
        if data['data']['type'] == 'BUFFER' or data['data']['type'] == 'CONTAINER':
            rows.append(html.Tr([html.Td(data['data']['type'], style=header_style), html.Td(data['data']['id'])]))
            rows.append(html.Tr([html.Td('Description:'), html.Td(data['data']['label'])]))
            amount = api_client.get('/get_amount_on_queue/' + data['data']['id'])
            rows.append(html.Tr([html.Td('Amount:'), html.Td(amount)]))
        elif data['classes'] == 'SENSOR':
            global sensor_ID
            sensor_ID = data['data']['id']
            rows.append(html.Tr([html.Td(data['classes'], style=header_style), html.Td(data['data']['id'])]))
            rows.append(html.Tr([html.Td('Description:'), html.Td(data['data']['label'])]))
            rows.append(html.Tr([html.Td('Type:'), html.Td(data['data']['type'])]))
        else:
            rows.append(html.Tr([html.Td(data['data']['type'], style=header_style), html.Td(data['data']['id'])]))
            rows.append(html.Tr([html.Td('Description:'), html.Td(data['data']['label'])]))

    table_body = [html.Tbody(rows)]
    table = dbc.Table(table_body, id='node_info-text', bordered=False)

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




