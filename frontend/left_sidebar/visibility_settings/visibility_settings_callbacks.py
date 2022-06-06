import helper_functions
from app import app
from dash.dependencies import Input, Output


@app.callback(Output('cytoscape-graph', 'stylesheet'),
              Input('switches-input', 'value'))
def update_output(value):
    """
    Toggles the visibility of element types in the main graph
    :param value:
    :return:
    """
    cystyle = helper_functions._load_json(app.get_asset_url('cy-style.json'))

    opacity_edges = 0
    opacity_parts = 0
    if 1 in value:
        opacity_edges = 1
    if 2 in value:
        opacity_parts = 1
    new_styles = [
        {
            'selector': 'edge',
            'style': {
                'opacity': opacity_edges
            }
        },
        {
            "selector": ".SINGLE_PART",
            'style': {
                'opacity': opacity_parts
            }
        },
        {
            "selector": ".PROCESSED_PART",
            'style': {
                'opacity': opacity_parts
            }
        },
        {
            "selector": ".part_edge",
            'style': {
                'opacity': opacity_parts
            }
        }
    ]
    print(value)
    return cystyle + new_styles
