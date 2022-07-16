import json
from typing import List
from graph_domain.DatabaseConnectionNode import DatabaseConnectionNode

from graph_domain.AssetNode import AssetNodeFlat, AssetNodeDeep
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


class DatabaseConnectionsDao(object):
    """
    Data Access Object for DatabaseConnections (KG-nodes representing)
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

        DatabaseConnectionsDao.__instance = self

        self.ps: KnowledgeGraphPersistenceService = (
            KnowledgeGraphPersistenceService.instance()
        )

    @validate_result_nodes
    def get_database_connections(self) -> List[DatabaseConnectionNode]:
        """
        Queries all database connection nodes. Does not follow any relationships
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        db_con_matches = self.ps.repo.match(model=DatabaseConnectionNode)
        db_cons = [m for m in db_con_matches]

        return db_cons

    @validate_result_nodes
    def get_database_connection_for_node(self, iri: str) -> DatabaseConnectionNode:
        """
        Gets the specific db connection for the node with the given iri, if available
        :param self:
        :param iri:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        # db_con_matches = self.ps.repo.match(model=DatabaseConnection)
        # db_cons = [m for m in db_con_matches]

        node = self.ps.graph.evaluate(
            f'MATCH p=(t)-[r:{RelationshipTypes.TIMESERIES_DB_ACCESS.value}|{RelationshipTypes.FILE_DB_ACCESS.value}]->(d:{NodeTypes.DATABASE_CONNECTION.value}) where (t.iri= "{iri}") RETURN d'
        )

        model = DatabaseConnectionNode.wrap(node)

        return model
