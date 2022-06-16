from dataclasses import dataclass

from dataclasses_json import dataclass_json
from py2neo.ogm import Model, Property


@dataclass
@dataclass_json
class BaseNode(Model):
    """
    Base node type defining properties every node has
    """

    # Core properties:
    id_short: str = Property()
    iri: str = Property()
    description: str = Property()

    # Additional properties for visualization (may initially be empty)
    visualization_positioning_x: float = Property(default=0.0)
    visualization_positioning_y: float = Property(default=0.0)

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        :return:
        """
        return self.id_short is not None and \
            self.iri is not None and \
            self.description is not None
