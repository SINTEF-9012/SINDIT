from app import app

from dash.dependencies import Input, Output, State
import requests
import plotly
import environment.settings as stngs
import helper_functions

API_URI = stngs.FAST_API_URI

@app.callback(Output('cytoscape-graph', 'elements'),
              Input('interval-component', 'n_intervals'))
def update_factory_graph(n):
    cygraph = requests.get(API_URI + '/get_factory_cytoscape_from_neo4j').json()
    return cygraph



@app.callback(Output('cytoscape-parts-graph', 'elements'),
              Input('cytoscape-graph', 'tapNode'))
def displayTapPartNodeData(data):
    parts_cygraph = []
    if data:
        print(data['data']['id'])
        if data['data']['type'] == 'SINGLE_PART' or data['data']['type'] == 'PROCESSED_PART':
            uuid = data['data']['id']
            parts_cygraph = requests.get(API_URI + '/get_part_cytoscape_from_neo4j/' + uuid).json()

    return parts_cygraph

@app.callback(Output('cytoscape-tapNodeData', 'children'),
              Input('cytoscape-graph', 'tapNode'),
              State('tabs-infos', 'value'),
              prevent_initial_call=True)
def displayTapNodeData(data, tab_name):
    if data['classes'] != 'SENSOR' and tab_name == 'tab-sensors':
        return None

    return helper_functions._draw_table_node_infos(data)