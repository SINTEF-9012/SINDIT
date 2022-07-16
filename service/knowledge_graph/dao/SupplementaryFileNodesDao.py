import json
from typing import List
from graph_domain.DatabaseConnectionNode import DatabaseConnectionNode

from graph_domain.AssetNode import AssetNodeFlat, AssetNodeDeep
from graph_domain.SupplementaryFileNode import SupplementaryFileNodeFlat
from graph_domain.factory_graph_types import NodeTypes, RelationshipTypes
from service.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)
from service.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from service.knowledge_graph.knowledge_graph_metamodel_validator import (
    validate_result_nodes,
)


class SupplementaryFileNodesDao(object):
    """
    Data Access Object for SupplementaryFiles (KG-nodes representing)
    """

    __instance = None

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls()
        return cls.__instance

    def __init__(self):
        if self.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        SupplementaryFileNodesDao.__instance = self

        self.ps: KnowledgeGraphPersistenceService = (
            KnowledgeGraphPersistenceService.instance()
        )

    @validate_result_nodes
    def get_supplementary_file_node_flat(
        self, iri: str
    ) -> List[DatabaseConnectionNode]:
        """
        Queries the specified supplementary file node. Does not follow any relationships
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        suppl_file_match = self.ps.repo.match(
            model=SupplementaryFileNodeFlat, primary_value=iri
        )

        return suppl_file_match.first()
