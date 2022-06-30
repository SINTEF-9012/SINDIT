from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, RelatedTo

from graph_domain.BaseNode import BaseNode
from graph_domain.UnitNode import UnitNode
from graph_domain.factory_graph_types import NodeTypes
from service.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)

LABEL = NodeTypes.DATABASE_CONNECTION.value


class DatabaseConnectionTypes(Enum):
    INFLUX_DB = "INFLUX_DB"


DATABASE_CONNECTION_TYPES = [con_type.value for con_type in DatabaseConnectionTypes]


@dataclass
@dataclass_json
class DatabaseConnectionNode(BaseNode):
    """
    Flat database connection node without relationships, only containing properties
    """

    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Additional properties:

    # Connectivity (Names of environment variables containing the actual information for security reasons):
    host_environment_variable: str = Property()
    port_environment_variable: str = Property()
    user_environment_variable: str | None = Property(
        default=None
    )  # may be None, if no authentication is required
    key_environment_variable: str | None = Property(
        default=None
    )  # may be None, if no authentication is required

    # Type of database
    type: str = Property()
    # For DBMS that allow multiple databases
    database: str | None = Property()  # may be none
    # Group / bucket in which the connections lay
    group: str | None = Property()  # may be none

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if self.type is None:
            raise GraphNotConformantToMetamodelError(self, f"Missing connection type.")

        if self.host_environment_variable is None:
            raise GraphNotConformantToMetamodelError(self, f"Missing host.")

        if self.port_environment_variable is None:
            raise GraphNotConformantToMetamodelError(self, f"Missing port.")

        if not self.type in DATABASE_CONNECTION_TYPES:
            raise GraphNotConformantToMetamodelError(
                self, f"Unrecognized connection type."
            )
