from dataclasses import dataclass
from enum import Enum
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, RelatedTo

from graph_domain.BaseNode import BaseNode
from graph_domain.DatabaseConnectionNode import DatabaseConnectionNode
from graph_domain.RuntimeConnectionNode import RuntimeConnectionNode
from graph_domain.UnitNode import UnitNode
from graph_domain.factory_graph_types import NodeTypes, RelationshipTypes
from service.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)

LABEL = NodeTypes.SUPPLEMENTARY_FILE.value
DB_CONNECTION_RELATIONSHIP_LABEL = RelationshipTypes.FILE_DB_ACCESS.value


class SupplementaryFileTypes(Enum):
    IMAGE_JPG = "IMAGE_JPG"
    CAD_STEP = "CAD_STEP"
    DOCUMENT_PDF = "DOCUMENT_PDF"


SUPPLEMENTARY_FILE_TYPES = [file_type.value for file_type in SupplementaryFileTypes]


@dataclass
@dataclass_json
class SupplementaryFileNodeFlat(BaseNode):
    """
    Flat supplementary file node without relationships, only containing properties
    """

    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Additional properties:
    file_name: str = Property()

    # Type of the value stored per time
    file_type: str = Property(default=SupplementaryFileTypes.DOCUMENT_PDF.value)

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if self.file_type is None:
            raise GraphNotConformantToMetamodelError(self, f"Missing file type.")

        if not self.file_type in SUPPLEMENTARY_FILE_TYPES:
            raise GraphNotConformantToMetamodelError(
                self,
                f"Unrecognized file type: {self.file_type}. Known types: {SUPPLEMENTARY_FILE_TYPES}.",
            )

        if self.file_name is None:
            raise GraphNotConformantToMetamodelError(self, f"Missing file name")


@dataclass
@dataclass_json
class SupplementaryFileNodeDeep(SupplementaryFileNodeFlat):
    """
    Deep supplementary file node with relationships
    """

    __primarylabel__ = LABEL

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _db_connections: List[DatabaseConnectionNode] = RelatedTo(
        DatabaseConnectionNode, DB_CONNECTION_RELATIONSHIP_LABEL
    )

    @property
    def db_connection(self) -> DatabaseConnectionNode:
        return [connection for connection in self._db_connections][0]

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if not len(self._db_connections) == 1:
            raise GraphNotConformantToMetamodelError(
                self,
                f"Invalid number of referenced database connections: {len(self._db_connections)}",
            )

        self.db_connection.validate_metamodel_conformance()
