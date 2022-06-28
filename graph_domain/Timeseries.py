from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, RelatedTo

from graph_domain.BaseNode import BaseNode
from graph_domain.DatabaseConnection import DatabaseConnection
from graph_domain.Unit import Unit
from graph_domain.factory_graph_types import NodeTypes, RelationshipTypes
from service.exceptions.GraphNotConformantToMetamodelError import GraphNotConformantToMetamodelError

LABEL = NodeTypes.TIMESERIES_INPUT.value
UNIT_RELATIONSHIP_LABEL = RelationshipTypes.HAS_UNIT.value
DB_CONNECTION_RELATIONSHIP_LABEL = RelationshipTypes.DB_ACCESS.value


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
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

@dataclass
@dataclass_json
class TimeseriesDeep(TimeseriesFlat):
    """
    Deep timeseries node with relationships
    """
    __primarylabel__ = LABEL

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _units: List[Unit] = RelatedTo(Unit, UNIT_RELATIONSHIP_LABEL)

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _connections: List[DatabaseConnection] = RelatedTo(DatabaseConnection, DB_CONNECTION_RELATIONSHIP_LABEL)

    @property
    def unit(self) -> Unit:
        return [unit for unit in self._units][0]
    
    @property
    def connection(self) -> DatabaseConnection:
        return [connection for connection in self._connections][0]

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if not len(self._units) == 1:
            raise GraphNotConformantToMetamodelError(self, f"Invalid number of referenced units: {len(self.__units)}")

        self.unit.validate_metamodel_conformance()
        
        if not len(self._connections) == 1:
            raise GraphNotConformantToMetamodelError(self, f"Invalid number of referenced database connections: {len(self.__connections)}")

        self.connection.validate_metamodel_conformance()

