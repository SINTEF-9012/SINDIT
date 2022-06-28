from dataclasses import dataclass
from enum import Enum

from dataclasses_json import dataclass_json
from py2neo.ogm import Property

from graph_domain.BaseNode import BaseNode
from graph_domain.factory_graph_types import NodeTypes
from service.exceptions.GraphNotConformantToMetamodelError import GraphNotConformantToMetamodelError

LABEL = NodeTypes.UNIT.value


@dataclass
@dataclass_json
class Unit(BaseNode):
    """
    Defines the unit of a timeseries
    Flat node without relationships, only containing properties.
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

        # if not self in [unit.value for unit in AllowedUnitsEnum]:
        #     raise GraphNotConformantToMetamodelError(self, "Unrecognized unit: Not in enum.")

# class AllowedUnitsEnum(Enum):
#     MILLIMETER = Unit(
#         id_short='mm',
#         iri='www.sintef.no/sindit/identifiers/units/mm',
#         description='Distance measurement in millimeters'
#     )
#     DEG_CELSIUS = Unit(
#         id_short='deg_celsius',
#         iri='www.sintef.no/sindit/identifiers/units/deg_celsius',
#         description='Temperature measurement in degrees celsius'
#     )