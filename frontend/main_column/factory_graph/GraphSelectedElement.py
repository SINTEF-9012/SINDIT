from dataclasses import dataclass
from dataclasses_json import dataclass_json

from frontend.main_column.factory_graph.factory_graph_types import SelectedElementTypes


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

    type: SelectedElementTypes = SelectedElementTypes.UNSPECIFIED
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

        if tap_edge["classes"] in [el_type.value for el_type in SelectedElementTypes]:
            el_type = tap_edge["classes"]
        else:
            print("Edge type not found! Fallback to unspecified.")
            el_type = SelectedElementTypes.UNSPECIFIED_EDGE_TYPE.value

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

        if tap_node["classes"] in [el_type.value for el_type in SelectedElementTypes]:
            el_type = tap_node["classes"]
        else:
            print("Node type not found! Fallback to unspecified.")
            el_type = SelectedElementTypes.UNSPECIFIED_NODE_TYPE.value

        return cls(
            id_short=tap_node['data']['id'],
            iri=tap_node['data']['iri'],
            type=el_type,
            is_node=True,
            position_x=tap_node['position']['x'],
            position_y=tap_node['position']['y']
        )
