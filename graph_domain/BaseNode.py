from dataclasses import dataclass

from dataclasses_json import dataclass_json
from py2neo.ogm import Model, Property


@dataclass
@dataclass_json
class BaseNode(Model):
    """
    Base node type defining properties every node has
    """

    id_short: str = Property()
    iri: str = Property()
    description: str = Property()
