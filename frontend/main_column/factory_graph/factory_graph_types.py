from enum import Enum

from graph_domain import Machine, Timeseries, DatabaseConnection, Unit

class SelectedElementTypes(Enum):
    # Node Types
    MACHINE = Machine.LABEL
    TIMESERIES_INPUT = Timeseries.LABEL
    DATABASE_CONNECTION = DatabaseConnection.LABEL
    UNIT = Unit.LABEL
    UNSPECIFIED_NODE_TYPE = 'UNSPECIFIED_NODE_TYPE'
    # Edge Types
    HAS_TIMESERIES = 'HAS_TIMESERIES'
    ALL_TIME_ACCESS = 'ALL_TIME_ACCESS'
    HAS_UNIT = 'HAS_UNIT'
    UNSPECIFIED_EDGE_TYPE = 'UNSPECIFIED_EDGE_TYPE'
    # Generic
    UNSPECIFIED = 'UNSPECIFIED'
