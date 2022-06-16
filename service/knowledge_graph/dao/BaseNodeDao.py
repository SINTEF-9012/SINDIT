import json

from py2neo import Node, NodeMatcher

from graph_domain.Machine import MachineFlat, MachineDeep
from service.exceptions.GraphNotConformantToMetamodelError import GraphNotConformantToMetamodelError
from service.knowledge_graph.KnowledgeGraphPersistenceService import KnowledgeGraphPersistenceService
from service.knowledge_graph.knowledge_graph_metamodel_validator import validate_result_node_list


class BaseNodeDao(object):
    """
    Data Access Object for Machines
    """
    __instance = None

    @staticmethod
    def instance():
        if BaseNodeDao.__instance is None:
            BaseNodeDao()
        return BaseNodeDao.__instance

    def __init__(self):
        if BaseNodeDao.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        BaseNodeDao.__instance = self

        self.ps: KnowledgeGraphPersistenceService = KnowledgeGraphPersistenceService.instance()

    def update_node_position(self, iri: str, new_pos_x: float, new_pos_y: float):
        """
        Stores a new position for the node
        :param iri:
        :param new_pos_x:
        :param new_pos_y:
        :return:
        """
        matcher = NodeMatcher(self.ps.graph)
        node: Node = matcher.match(iri=iri).first()
        node.update(visualization_positioning_x=new_pos_x, visualization_positioning_y=new_pos_y)
        self.ps.graph.push(node)
