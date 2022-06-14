import random

from dash.dependencies import Input, Output, State

from frontend import api_client
from frontend.app import app
from frontend.main_column.factory_graph import factory_graph_layout
from graph_domain.Machine import MachineDeep

print("Initializing factory graph callbacks...")


# @app.callback(Output('cytoscape-graph', 'elements'),
#               Input('interval-component', 'n_intervals'))
# def update_factory_graph(n):
#     cygraph = api_client.get('/get_factory_cytoscape_from_neo4j')
#     return cygraph

# Auto layout test:
# @app.callback(Output('cytoscape-graph', 'layout'),
#               Input('interval-component', 'n_intervals'))
# def update_layout(layout):
#     layout_options =  ['grid', 'random', 'circle', 'cose', 'concentric']
#
#     random_index = random.randint(0, len(layout_options))
#
#     return {
#         'name': layout_options[random_index],
#         'animate': True
#     }

@app.callback(Output('cytoscape-graph', 'elements'),
              Input('interval-component', 'n_intervals'))
def update_factory_graph(n):
    machines_deep_json = api_client.get('/graph/machines_deep')

    machines_deep = [MachineDeep.from_json(m) for m in machines_deep_json]

    cygraph_elements = factory_graph_layout.get_cytoscape_elements(machines_deep=machines_deep)

    # return [{'data': {'id': 'M1_1', 'label': 'Cocoa butter melting', 'type': 'MACHINE', 'parent': []}, 'group': 'nodes', 'classes': 'MACHINE', 'position': {'x': -230, 'y': 35}, 'style': {'shape': 'round-rectangle', 'background-color': '#b19cd9', 'height': 20, 'width': 30}}, {'data': {'id': 'S1_1', 'label': 'SINDIT Sensor', 'type': 'temperature'}, 'group': 'nodes', 'classes': 'SENSOR', 'position': {'x': -221.0, 'y': 41.0}}, {'data': {'id': 'M1_2', 'label': 'Sugar grinding', 'type': 'MACHINE', 'parent': []}, 'group': 'nodes', 'classes': 'MACHINE', 'position': {'x': -230, 'y': 100}, 'style': {'shape': 'round-rectangle', 'background-color': '#b19cd9', 'height': 20, 'width': 30}}, {'data': {'id': 'S1_2', 'label': 'SINDIT Sensor', 'type': 'temperature'}, 'group': 'nodes', 'classes': 'SENSOR', 'position': {'x': -221.0, 'y': 106.0}}, {'data': {'id': 'M2', 'label': 'Conching', 'type': 'MACHINE', 'parent': []}, 'group': 'nodes', 'classes': 'MACHINE', 'position': {'x': -145, 'y': 70}, 'style': {'shape': 'round-rectangle', 'background-color': '#b19cd9', 'height': 20, 'width': 30}}, {'data': {'id': 'S2_1', 'label': 'SINDIT Sensor', 'type': 'temperature'}, 'group': 'nodes', 'classes': 'SENSOR', 'position': {'x': -136.0, 'y': 76.0}}, {'data': {'id': 'M3', 'label': 'Chocolate paste tempering', 'type': 'MACHINE', 'parent': []}, 'group': 'nodes', 'classes': 'MACHINE', 'position': {'x': -73, 'y': 70}, 'style': {'shape': 'round-rectangle', 'background-color': '#b19cd9', 'height': 20, 'width': 30}}, {'data': {'id': 'S3_1', 'label': 'SINDIT Sensor', 'type': 'temperature'}, 'group': 'nodes', 'classes': 'SENSOR', 'position': {'x': -64.0, 'y': 76.0}}, {'data': {'id': 'M4', 'label': 'Shell moulding', 'type': 'MACHINE', 'parent': []}, 'group': 'nodes', 'classes': 'MACHINE', 'position': {'x': 5, 'y': 70}, 'style': {'shape': 'round-rectangle', 'background-color': '#b19cd9', 'height': 20, 'width': 30}}, {'data': {'id': 'S4_1', 'label': 'SINDIT Sensor', 'type': 'temperature'}, 'group': 'nodes', 'classes': 'SENSOR', 'position': {'x': 14.0, 'y': 76.0}}, {'data': {'id': 'M5', 'label': 'Packaging', 'type': 'MACHINE', 'parent': []}, 'group': 'nodes', 'classes': 'MACHINE', 'position': {'x': 82, 'y': 70}, 'style': {'shape': 'round-rectangle', 'background-color': '#b19cd9', 'height': 20, 'width': 30}}, {'data': {'id': 'S5_1', 'label': 'SINDIT Sensor', 'type': 'vibration'}, 'group': 'nodes', 'classes': 'SENSOR', 'position': {'x': 91.0, 'y': 76.0}}, {'data': {'id': 'S1', 'label': 'Cocoa butter', 'type': 'SOURCE', 'parent': []}, 'group': 'nodes', 'classes': 'SOURCE', 'position': {'x': -305, 'y': 35}, 'style': {'shape': 'round-rectangle', 'background-color': '#b19cd9', 'height': 20, 'width': 30}}, {'data': {'id': 'S2', 'label': 'Sugar', 'type': 'SOURCE', 'parent': []}, 'group': 'nodes', 'classes': 'SOURCE', 'position': {'x': -305, 'y': 100}, 'style': {'shape': 'round-rectangle', 'background-color': '#b19cd9', 'height': 20, 'width': 30}}, {'data': {'id': 'S3', 'label': 'Packaging', 'type': 'SOURCE', 'parent': []}, 'group': 'nodes', 'classes': 'SOURCE', 'position': {'x': 80, 'y': 10}, 'style': {'shape': 'round-rectangle', 'background-color': '#b19cd9', 'height': 20, 'width': 30}}, {'data': {'id': 'E1', 'label': 'Product exit', 'type': 'EXIT', 'parent': []}, 'group': 'nodes', 'classes': 'EXIT', 'position': {'x': 80, 'y': 143}, 'style': {'shape': 'round-rectangle', 'background-color': '#b19cd9', 'height': 20, 'width': 30}}, {'data': {'id': 'Q7', 'label': 'Moulded chocolate bars', 'type': 'BUFFER', 'weight': 0, 'color': 'green', 'parent': []}, 'group': 'nodes', 'classes': 'BUFFER', 'position': {'x': 42, 'y': 70}, 'style': {'shape': 'round-rectangle', 'background-color': '#efcc61', 'height': 5, 'width': 10}}, {'data': {'id': 'Q9', 'label': 'Packaged chocolate bars', 'type': 'BUFFER', 'weight': 0, 'color': 'green', 'parent': []}, 'group': 'nodes', 'classes': 'BUFFER', 'position': {'x': 80, 'y': 105}, 'style': {'shape': 'round-rectangle', 'background-color': '#efcc61', 'height': 5, 'width': 10}}, {'data': {'id': 'Q2', 'label': 'Raw cocoa butter', 'type': 'CONTAINER', 'weight': 100, 'color': 'green', 'parent': []}, 'group': 'nodes', 'classes': 'CONTAINER', 'position': {'x': -305, 'y': 35}, 'style': {'shape': 'round-rectangle', 'background-color': '#efcc61', 'height': 5, 'width': 10}}, {'data': {'id': 'Q1', 'label': 'Raw sugar', 'type': 'CONTAINER', 'weight': 100, 'color': 'green', 'parent': []}, 'group': 'nodes', 'classes': 'CONTAINER', 'position': {'x': -305, 'y': 100}, 'style': {'shape': 'round-rectangle', 'background-color': '#efcc61', 'height': 5, 'width': 10}}, {'data': {'id': 'Q3', 'label': 'Melted cocoa butter', 'type': 'CONTAINER', 'weight': 0, 'color': 'green', 'parent': []}, 'group': 'nodes', 'classes': 'CONTAINER', 'position': {'x': -184, 'y': 35}, 'style': {'shape': 'round-rectangle', 'background-color': '#efcc61', 'height': 5, 'width': 10}}, {'data': {'id': 'Q4', 'label': 'Grinded sugar', 'type': 'CONTAINER', 'weight': 0, 'color': 'green', 'parent': []}, 'group': 'nodes', 'classes': 'CONTAINER', 'position': {'x': -184, 'y': 100}, 'style': {'shape': 'round-rectangle', 'background-color': '#efcc61', 'height': 5, 'width': 10}}, {'data': {'id': 'Q5', 'label': 'Conched chocolate paste', 'type': 'CONTAINER', 'weight': 0, 'color': 'green', 'parent': []}, 'group': 'nodes', 'classes': 'CONTAINER', 'position': {'x': -109, 'y': 70}, 'style': {'shape': 'round-rectangle', 'background-color': '#efcc61', 'height': 5, 'width': 10}}, {'data': {'id': 'Q6', 'label': 'Tempered chocolate paste', 'type': 'CONTAINER', 'weight': 0, 'color': 'green', 'parent': []}, 'group': 'nodes', 'classes': 'CONTAINER', 'position': {'x': -35, 'y': 70}, 'style': {'shape': 'round-rectangle', 'background-color': '#efcc61', 'height': 5, 'width': 10}}, {'data': {'id': 'Q8', 'label': 'Packaging material', 'type': 'CONTAINER', 'weight': 100, 'color': 'green', 'parent': []}, 'group': 'nodes', 'classes': 'CONTAINER', 'position': {'x': 80, 'y': 40}, 'style': {'shape': 'round-rectangle', 'background-color': '#efcc61', 'height': 5, 'width': 10}}, {'data': {'source': 'M4', 'target': 'Q7'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'Q7', 'target': 'M5'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'M5', 'target': 'Q9'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'Q9', 'target': 'E1'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'S1', 'target': 'Q2'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'Q2', 'target': 'M1_1'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'S2', 'target': 'Q1'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'Q1', 'target': 'M1_2'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'M1_1', 'target': 'Q3'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'Q3', 'target': 'M2'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'M1_2', 'target': 'Q4'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'Q4', 'target': 'M2'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'M2', 'target': 'Q5'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'Q5', 'target': 'M3'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'M3', 'target': 'Q6'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'Q6', 'target': 'M4'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'S3', 'target': 'Q8'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'Q8', 'target': 'M5'}, 'classes': 'machine_edge', 'group': 'edges'}, {'data': {'source': 'M1_1', 'target': 'S1_1'}, 'classes': 'sensor_edge', 'style': {}, 'group': 'edges'}, {'data': {'source': 'M1_2', 'target': 'S1_2'}, 'classes': 'sensor_edge', 'style': {}, 'group': 'edges'}, {'data': {'source': 'M2', 'target': 'S2_1'}, 'classes': 'sensor_edge', 'style': {}, 'group': 'edges'}, {'data': {'source': 'M3', 'target': 'S3_1'}, 'classes': 'sensor_edge', 'style': {}, 'group': 'edges'}, {'data': {'source': 'M4', 'target': 'S4_1'}, 'classes': 'sensor_edge', 'style': {}, 'group': 'edges'}, {'data': {'source': 'M5', 'target': 'S5_1'}, 'classes': 'sensor_edge', 'style': {}, 'group': 'edges'}]

    return cygraph_elements


    # cygraph_elements = []
    #
    # cygraph = api_client.get('/get_factory_cytoscape_from_neo4j')
    # return cygraph

    # return cygraph_elements

