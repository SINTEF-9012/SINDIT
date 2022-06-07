from dash import html
from dash.dependencies import Input, Output, State

from frontend.app import app
from frontend.right_sidebar.node_data_tab import node_data_layout
from frontend.styles import CustomStyles

print("Initializing navigation callbacks...")

@app.callback(Output('tabs-content', 'children'),
              Input('tabs-infos', 'value'),
              State('cytoscape-graph', 'tapNode'))
def change_navigation_tab(tab, tap_node):
    """
    Navigation through the tabs of the right sidebar
    :param tap_node:
    :param tab:
    :return:
    """
    # TODO: contents to own files..
    if tab == 'tab-node-information':
        return html.Div([
            html.Pre(id='cytoscape-tapNodeData', style=CustomStyles.PRE.value)
        ])
    elif tab == 'tab-node-data':
        return html.Div([
            # TODO: extract node-type and forward only this
            node_data_layout.get_layout(tap_node)
        ])

