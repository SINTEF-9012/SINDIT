from __future__ import annotations
from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, RelatedTo

from graph_domain.BaseNode import BaseNode
from graph_domain.Unit import Unit
from graph_domain.factory_graph_types import NodeTypes
from service.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)

LABEL = NodeTypes.DATABASE_CONNECTION.value

REALTIME_CONNECTION_TYPES = ["OPC_UA", "MQTT"]


@dataclass
@dataclass_json
class RuntimeConnection(BaseNode):
    """
    Flat runtime connection node without relationships, only containing properties
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

    # Type of connection
    type: str = Property()

    # Info: the actual host, port and if required passwords are not provided by the context-graph but via environmental variables instead

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

        if not self.type in REALTIME_CONNECTION_TYPES:
            raise GraphNotConformantToMetamodelError(
                self, f"Unrecognized connection type."
            )
