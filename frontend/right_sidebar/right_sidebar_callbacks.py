from dash import html
from dash.dependencies import Input, Output, State

from frontend.app import app
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.node_data_tab import node_data_layout

print("Initializing navigation callbacks...")

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs-infos', 'value'),
               Input('selected-graph-element-store', 'data')])
def change_navigation_tab(tab, selected_el_json):
    """
    Navigation through the tabs of the right sidebar
    :param selected_el_json:
    :param tab:
    :return:
    """
    if selected_el_json is None:
        selected_el = None
    else:
        selected_el = GraphSelectedElement.from_json(selected_el_json)

    # TODO: contents to own files..
    if tab == 'tab-node-information':
        return html.Div(
            children=[
                "Will contain iri, description, ..."
                # TODO: standard details about the selected node...
            ],
            className='tab-content-container'
        )
    elif tab == 'tab-node-data':
        return html.Div(
            children=[
                node_data_layout.get_layout(selected_el)
            ],
            className='tab-content-container'
        )

