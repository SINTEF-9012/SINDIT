from enum import Enum
from itertools import chain


class NodeTypes(Enum):
    MACHINE = "MACHINE"
    TIMESERIES_INPUT = "TIMESERIES"
    DATABASE_CONNECTION = "DATABASE_CONNECTION"
    RUNTIME_CONNECTION = "RUNTIME_CONNECTION"
    UNIT = "UNIT"


class RelationshipTypes(Enum):
    HAS_TIMESERIES = "HAS_TIMESERIES"
    DB_ACCESS = "DB_ACCESS"
    RUNTIME_ACCESS = "RUNTIME_ACCESS"
    HAS_UNIT = "HAS_UNIT"


NODE_TYPE_STRINGS = [nd_type.value for nd_type in NodeTypes]
RELATIONSHIP_TYPE_STRINGS = [rl_type.value for rl_type in RelationshipTypes]
ELEMENT_TYPE_STRINGS = list(chain(NODE_TYPE_STRINGS, RELATIONSHIP_TYPE_STRINGS))

UNSPECIFIED_LABEL = "UNSPECIFIED"

RELATIONSHIP_TYPES_FOR_NODE_TYPE = {
    NodeTypes.MACHINE.value: [RelationshipTypes.HAS_TIMESERIES.value],
    NodeTypes.TIMESERIES_INPUT.value: [
        RelationshipTypes.HAS_TIMESERIES.value,
        RelationshipTypes.HAS_UNIT.value,
        RelationshipTypes.RUNTIME_ACCESS.value,
    ],
    NodeTypes.DATABASE_CONNECTION.value: [RelationshipTypes.DB_ACCESS.value],
    NodeTypes.UNIT.value: [RelationshipTypes.HAS_UNIT.value],
    NodeTypes.RUNTIME_CONNECTION.value: [RelationshipTypes.RUNTIME_ACCESS.value],
}
