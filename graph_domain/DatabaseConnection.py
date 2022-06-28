from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, RelatedTo

from graph_domain.BaseNode import BaseNode
from graph_domain.Unit import Unit
from graph_domain.factory_graph_types import NodeTypes
from service.exceptions.GraphNotConformantToMetamodelError import GraphNotConformantToMetamodelError

LABEL = NodeTypes.DATABASE_CONNECTION.value

DATABASE_CONNECTION_TYPES = [
    "INFLUX_DB"
]

@dataclass
@dataclass_json
class DatabaseConnection(BaseNode):
    """
    Flat database connection node without relationships, only containing properties
    """
    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Additional properties:

    # Type of database
    type: str = Property()
    # For DBMS that allow multiple databases
    database: str = Property()  # may be none
    # Group / bucket in which the connections lay
    group: str = Property()  # may be none

    # Info: the actual host, port and if required passwords are not provided by the context-graph but via environmental variables instead

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if self.type is None:
            raise GraphNotConformantToMetamodelError(self, f"Missing connection type.")

        if not self.type in DATABASE_CONNECTION_TYPES:
            raise GraphNotConformantToMetamodelError(self, f"Unrecognized connection type.")
