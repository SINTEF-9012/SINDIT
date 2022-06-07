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


def _generate_sensor_data(duration_h=3):
    date_rng = pd.date_range(start=pd.Timestamp(datetime.datetime.now() - datetime.timedelta(hours=duration_h)),
                             end=pd.Timestamp(datetime.datetime.now()), freq='1T')

    df = pd.DataFrame(date_rng, columns=['time_ms'])
    df['data 0'] = np.random.randint(0, 50, size=(len(date_rng)))
    df['data 1'] = np.random.randint(0, 100, size=(len(date_rng)))

    time_ms_array = np.zeros(len(date_rng))
    for index, row in df.iterrows():
        time_ms_array[index] = int(row['time_ms'].timestamp() * 1000)

    df['data 2'] = np.sin(time_ms_array) * 70
    df['data 3'] = np.random.randint(0, 100, size=(len(date_rng))) + np.sin(time_ms_array) * 5

    sensor_readings = pd.DataFrame(data={'value': df['data ' + str(random.randint(0, 3))].to_numpy().tolist(), \
                                         'timestamp': pd.to_datetime(time_ms_array, unit='ms')})

    return json.loads(sensor_readings.to_json(orient="records"))


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
            amount = api_client.get_json('/get_amount_on_queue/' + data['data']['id'])
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




