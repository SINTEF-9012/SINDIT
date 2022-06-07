from frontend.right_sidebar.node_data_tab.live_sensor_readings import sensor_readings_layout


def get_layout(node_type):
    """
    Layout of the node-data tab: e.g. real time sensor data. Dependent on the selected node type
    :param node_type:
    :return:
    """

    # TODO: return node-type specific details page
    return sensor_readings_layout.get_layout()

