from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, RelatedTo

from graph_domain.BaseNode import BaseNode
from graph_domain.Unit import Unit

LABEL = 'TIMESERIES'


@dataclass
@dataclass_json
class TimeseriesFlat(BaseNode):
    """
    Flat timeseries node without relationships, only containing properties
    """
    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Additional properties:

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        :return:
        """
        return super().validate_metamodel_conformance()


@dataclass
@dataclass_json
class TimeseriesDeep(TimeseriesFlat):
    """
    Deep timeseries node with relationships
    """
    __primarylabel__ = LABEL

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    units: List[Unit] = RelatedTo(Unit, "HAS_UNIT")

    # TODO: connectors...

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        :return:
        """
        return super().validate_metamodel_conformance() and \
            len(self.units) == 1 and \
            all(unit.validate_metamodel_conformance() for unit in self.units)
