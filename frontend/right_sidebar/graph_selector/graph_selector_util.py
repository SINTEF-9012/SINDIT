import json
from enum import Enum
"""
Util functions to store and receive info about the selected graph element

Example structure of the storage:

{
    'id_short': 'example_identifier_short',
    'iri': 'www.example.com/identifier/example_identifier',
    'description': 'some text...',
    'type': 'MACHINE',  # in SelectedElementTypes.values
    'node_edge': 'NODE'  # in NodeEdge.values
}
"""

class NodeEdge(Enum):
    NODE = 'NODE'
    EDGE = 'EDGE'
    UNSPECIFIED = 'UNSPECIFIED'

class SelectedElementTypes(Enum):
    # Node Types
    MACHINE = 'MACHINE'
    TIMESERIES_INPUT = 'SENSOR'  # TODO: change to "TIMESERIES"
    UNSPECIFIED_NODE_TYPE = 'UNSPECIFIED_NODE_TYPE'
    # Edge Types
    HAS_TIMESERIES = 'HAS_TIMESERIES'
    UNSPECIFIED_EDGE_TYPE = 'UNSPECIFIED_EDGE_TYPE'


def tap_edge_to_store(tap_edge):
    """
    :param tap_edge: cytoscape-graph tapEdge
    :return: json containing the structured information from the selected edge
    """
    if tap_edge is None:
        return ""

    if tap_edge["classes"] in [el_type.value for el_type in SelectedElementTypes]:
        el_type = tap_edge["classes"]
    else:
        print("Edge type not found! Fallback to unspecified.")
        el_type = SelectedElementTypes.UNSPECIFIED_EDGE_TYPE.value

    storage_dict = {
        'id_short': 'example_identifier_short',
        'iri': 'www.example.com/identifier/example_identifier',  # TODO
        'description': 'some description...',  # TODO
        'type': el_type,
        'node_edge': NodeEdge.EDGE.value
    }

    return json.dumps(storage_dict)


def tap_node_to_store(tap_node):
    """
    :param tap_node: cytoscape-graph tapNode
    :return: json containing the structured information from the selected node
    """
    if tap_node is None:
        return ""

    if tap_node["classes"] in [el_type.value for el_type in SelectedElementTypes]:
        el_type = tap_node["classes"]
    else:
        print("Node type not found! Fallback to unspecified.")
        el_type = SelectedElementTypes.UNSPECIFIED_NODE_TYPE.value

    storage_dict = {
        'id_short': 'example_identifier_short',
        'iri': 'www.sintef.no/asset_identifiers/fischertechnik_learning_factory/sensor_inputs/'
               'HBW/di_PosBelt_Horizontal',  # TODO
        'description': 'some description...',  # TODO
        'type': el_type,
        'node_edge': NodeEdge.NODE.value
    }

    return json.dumps(storage_dict)


# Getters:

def get_dict(selected_el_json):
    return json.loads(selected_el_json)


def get_id_short(selected_el_json):
    return get_dict(selected_el_json)['id_short']


def get_iri(selected_el_json):
    return get_dict(selected_el_json)['iri']


def get_description(selected_el_json):
    return get_dict(selected_el_json)['description']


def get_node_edge(selected_el_json):
    node_edge_str = get_dict(selected_el_json)['node_edge']

    for node_edge in NodeEdge:
        if node_edge_str == node_edge.value:
            return node_edge

    return NodeEdge.UNSPECIFIED


def get_type(selected_el_json):
    type_str = get_dict(selected_el_json)['type']

    for el_type in SelectedElementTypes:
        if type_str == el_type.value:
            return el_type

    if get_node_edge(selected_el_json) == NodeEdge.EDGE:
        return SelectedElementTypes.UNSPECIFIED_EDGE_TYPE
    else:
        return SelectedElementTypes.UNSPECIFIED_NODE_TYPE
