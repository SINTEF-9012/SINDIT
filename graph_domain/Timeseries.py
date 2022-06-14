from dataclasses import dataclass
from dataclasses_json import dataclass_json
from py2neo.ogm import Property

from graph_domain.BaseNode import BaseNode

LABEL = 'TIMESERIES'

@dataclass
@dataclass_json
class TimeseriesFlat(BaseNode):
    """
    Flat timeseries node without relationships, only containing properties
    """
    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Properties:



@dataclass
@dataclass_json
class TimeseriesDeep(TimeseriesFlat):
    """
    Deep timeseries node with relationships
    """
    __primarylabel__ = LABEL

    # TODO: connectors...
