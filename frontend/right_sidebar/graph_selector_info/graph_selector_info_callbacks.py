from dash.dependencies import Input, Output

from frontend.app import app
from frontend.right_sidebar.graph_selector_info import graph_selector_info_layout

print("Initializing graph selector callbacks...")


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
    return graph_selector_info_layout.get_info_content(selected_el)
