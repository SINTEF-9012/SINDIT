from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Model, Property, RelatedTo

from graph_domain.BaseNode import BaseNode
from graph_domain.SupplementaryFileNode import SupplementaryFileNodeDeep
from graph_domain.TimeseriesNode import TimeseriesNodeDeep
from graph_domain.factory_graph_types import NodeTypes, RelationshipTypes

LABEL = NodeTypes.ASSET.value
TIMESERIES_RELATIONSHIP = RelationshipTypes.HAS_TIMESERIES.value
SUPPLEMENTARY_FILE_RELATIONSHIP = RelationshipTypes.HAS_SUPPLEMENTARY_FILE.value


@dataclass
@dataclass_json
class AssetNodeFlat(BaseNode):
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
class AssetNodeDeep(AssetNodeFlat):
    """
    Deep machine node with relationships
    """

    __primarylabel__ = LABEL

    _timeseries: List[TimeseriesNodeDeep] = RelatedTo(
        TimeseriesNodeDeep, TIMESERIES_RELATIONSHIP
    )

    @property
    def timeseries(self) -> List[TimeseriesNodeDeep]:
        return [timeseries for timeseries in self._timeseries]

    _supplementary_files: List[SupplementaryFileNodeDeep] = RelatedTo(
        SupplementaryFileNodeDeep, SUPPLEMENTARY_FILE_RELATIONSHIP
    )

    @property
    def supplementary_files(self) -> List[SupplementaryFileNodeDeep]:
        return [suppl_file for suppl_file in self._supplementary_files]

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        for timeseries in self.timeseries:
            timeseries.validate_metamodel_conformance()

        for suppl_file in self.supplementary_files:
            suppl_file.validate_metamodel_conformance()
