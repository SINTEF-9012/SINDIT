from dash import html

from frontend.main_column.factory_graph import graph_selector_util
from frontend.right_sidebar.node_data_tab.live_sensor_readings import sensor_readings_layout


def get_layout(selected_el):
    """
    Layout of the node-data tab: e.g. real time sensor data. Dependent on the selected node type
    :param selected_el:
    :return:
    """

    if selected_el is None:
        # No node selected
        return html.Div(
            'Select a node to visualize its data'
        )
    elif selected_el.type == graph_selector_util.SelectedElementTypes.TIMESERIES_INPUT:
        return sensor_readings_layout.get_layout()
    else:
        # No data for this type of node
        return html.Div(
            'No data can be visualized for this type of node.'
        )
