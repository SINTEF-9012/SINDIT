from dash import html

from frontend.right_sidebar.node_data_tab.timeseries_graph import (
    timeseries_graph_layout,
)
from frontend.right_sidebar.node_data_tab.file_visualization import (
    file_visualization_layout,
)
from graph_domain.factory_graph_types import NodeTypes


def get_layout(selected_el):
    """
    Layout of the node-data tab: e.g. real time sensor data. Dependent on the selected node type
    :param selected_el:
    :return:
    """

    if selected_el is None:
        # No node selected
        return html.Div("Select a node to visualize its data")
    elif selected_el.type == NodeTypes.TIMESERIES_INPUT.value:
        return timeseries_graph_layout.get_layout()
    elif selected_el.type == NodeTypes.SUPPLEMENTARY_FILE.value:
        return file_visualization_layout.get_layout()
    else:
        # No data for this type of node
        return html.Div("No data can be visualized for this selection.")
