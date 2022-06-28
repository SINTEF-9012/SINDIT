from dataclasses import dataclass
from itertools import chain
from dataclasses_json import dataclass_json

from graph_domain.factory_graph_types import ELEMENT_TYPE_STRINGS, UNSPECIFIED_LABEL, NodeTypes, RelationshipTypes


# Take care: the order of this annotations makes a difference. Does not work with @dataclass before @dataclass_json
@dataclass_json
@dataclass
class GraphSelectedElement(object):
    """
    Information about one selectable element (node or edge) from the graph.
    Used to store and receive info about the selected graph element
    """

    # Core properties:
    id_short: str = None
    iri: str = None

    type: str = UNSPECIFIED_LABEL
    is_node: bool = None

    # Only for nodes:
    position_x: float = None
    position_y: float = None

    @classmethod
    def from_tap_edge(cls, tap_edge):
        """
        :param tap_edge: cytoscape-graph tapEdge
        :return: GraphSelectedElement
        """

        if tap_edge is None:
            return ""

        if tap_edge["classes"] in ELEMENT_TYPE_STRINGS:
            el_type = tap_edge["classes"]
        else:
            print("Edge type not found!")
            el_type = UNSPECIFIED_LABEL

        return GraphSelectedElement(
            id_short='NA',
            iri='NA',
            type=el_type,
            is_node=False
        )

    @classmethod
    def from_tap_node(cls, tap_node):
        """
        :param tap_node: cytoscape-graph tapNode
        :return: GraphSelectedElement
        """

        if tap_node is None:
            return ""

        if tap_node["classes"] in ELEMENT_TYPE_STRINGS:
            el_type = tap_node["classes"]
        else:
            print("Node type not found! Fallback to unspecified.")
            el_type = UNSPECIFIED_LABEL

        return cls(
            id_short=tap_node['data']['id'],
            iri=tap_node['data']['iri'],
            type=el_type,
            is_node=True,
            position_x=tap_node['position']['x'],
            position_y=tap_node['position']['y']
        )
