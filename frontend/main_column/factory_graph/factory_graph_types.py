from enum import Enum


class NodeEdge(Enum):
    NODE = 'NODE'
    EDGE = 'EDGE'
    UNSPECIFIED = 'UNSPECIFIED'

class SelectedElementTypes(Enum):
    # Node Types
    MACHINE = 'MACHINE'
    TIMESERIES_INPUT = 'TIMESERIES'
    UNSPECIFIED_NODE_TYPE = 'UNSPECIFIED_NODE_TYPE'
    # Edge Types
    HAS_TIMESERIES = 'HAS_TIMESERIES'
    UNSPECIFIED_EDGE_TYPE = 'UNSPECIFIED_EDGE_TYPE'
