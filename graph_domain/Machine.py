from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Model, Property, RelatedTo

from graph_domain.BaseNode import BaseNode
from graph_domain.Timeseries import TimeseriesDeep

LABEL = 'MACHINE'

@dataclass
@dataclass_json
class MachineFlat(BaseNode):
    """
    Flat machine node without relationships, only containing properties
    """
    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Additional properties:

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()


@dataclass
@dataclass_json
class MachineDeep(MachineFlat):
    """
    Deep machine node with relationships
    """
    __primarylabel__ = LABEL

    _timeseries: List[TimeseriesDeep] = RelatedTo(TimeseriesDeep, "HAS_TIMESERIES")

    @property
    def timeseries(self) -> List[TimeseriesDeep]:
        return [timeseries for timeseries in self._timeseries]

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        for timeseries in self.timeseries:
            timeseries.validate_metamodel_conformance()
