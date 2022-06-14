from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Model, Property, RelatedTo

from graph_domain.Timeseries import TimeseriesDeep

LABEL = 'MACHINE'

@dataclass
@dataclass_json
class MachineFlat(Model):
    """
    Flat machine node without relationships, only containing properties
    """
    # Identifier for the node-type:
    __primarylabel__ = LABEL

    id_short: str = Property()
    iri: str = Property()
    description: str = Property()


@dataclass
@dataclass_json
class MachineDeep(MachineFlat):
    """
    Deep machine node with relationships
    """
    __primarylabel__ = LABEL

    timeseries: List[TimeseriesDeep] = RelatedTo(TimeseriesDeep, "HAS_TIMESERIES")
