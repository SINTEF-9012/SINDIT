from dash.dependencies import Input, Output

from frontend.app import app
from frontend.right_sidebar.graph_selector import graph_selector_layout, graph_selector_util

print("Initializing graph selector callbacks...")


@app.callback(Output('selected-graph-element-store', 'data'),
              [Input('cytoscape-graph', 'tapNode'),
               Input('cytoscape-graph', 'tapEdge')],
              prevent_initial_call=True)
def store_selected_element_info(tap_node, tap_edge):
    """
    Called whenever a element in the graph is selected
    :param tap_edge:
    :param tap_node:
    :return:
    """
    if tap_edge is None or\
            tap_node is not None and tap_node['timeStamp'] > tap_edge['timeStamp']:
        # Node selected last:
        return graph_selector_util.tap_node_to_store(tap_node)
    else:
        # Edge selected last:
        return graph_selector_util.tap_edge_to_store(tap_edge)


@app.callback(Output('selected-graph-element-info', 'children'),
              Input('selected-graph-element-store', 'data'),
              prevent_initial_call=True)
def display_selected_graph_element_info(selected_el):
    """
    Called whenever a element in the graph is selected.
    Refreshes the user output with id, type, ...
    :param selected_el:
    :return:
    """
    return graph_selector_layout.get_info_content(selected_el)
