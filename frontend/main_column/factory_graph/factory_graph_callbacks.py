from dash.dependencies import Input, Output, State

import helper_functions
from frontend import api_client
from frontend.app import app

print("Initializing factory graph callbacks...")


@app.callback(Output('cytoscape-graph', 'elements'),
              Input('interval-component', 'n_intervals'))
def update_factory_graph(n):
    cygraph = api_client.get('/get_factory_cytoscape_from_neo4j')
    return cygraph
