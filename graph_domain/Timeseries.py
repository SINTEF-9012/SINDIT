from dataclasses import dataclass

from dataclasses_json import dataclass_json
from py2neo.ogm import Model, Property

LABEL = 'TIMESERIES'

@dataclass
@dataclass_json
class TimeseriesFlat(Model):
    """
    Flat timeseries node without relationships, only containing properties
    """
    # Identifier for the node-type:
    __primarylabel__ = LABEL

    id_short: str = Property()
    iri: str = Property()
    description: str = Property()


@dataclass
@dataclass_json
class TimeseriesDeep(TimeseriesFlat):
    """
    Deep timeseries node with relationships
    """
    __primarylabel__ = LABEL

    # TODO: connectors...
