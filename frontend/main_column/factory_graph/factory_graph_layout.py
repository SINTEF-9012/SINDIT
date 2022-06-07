from dash import html
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from frontend.app import app
from frontend import resources_manager, api_client

CY_STYLE_STATIC = resources_manager.load_json('cy-style.json')

def get_layout():
    cygraph = api_client.get('/get_factory_cytoscape_from_neo4j')
    # TODO: new api and path in separate config

    return html.Div([
        dbc.Card([
            dbc.CardHeader("Factory graph"),
            dbc.CardBody([
                cyto.Cytoscape(
                    id='cytoscape-graph',
                    layout={'name': 'preset'},
                    style={'width': '100%', 'height': '770px'},
                    stylesheet=CY_STYLE_STATIC,
                    elements=cygraph)
            ])
        ]),
    ])

