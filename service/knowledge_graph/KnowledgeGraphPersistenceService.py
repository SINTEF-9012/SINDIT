import py2neo
import py2neo.ogm as ogm

from config import global_config as cfg

import environment.environment as env


class KnowledgeGraphPersistenceService(object):
    """

    """
    __instance = None

    @staticmethod
    def instance():
        if KnowledgeGraphPersistenceService.__instance is None:
            KnowledgeGraphPersistenceService()
        return KnowledgeGraphPersistenceService.__instance

    def __init__(self):
        if KnowledgeGraphPersistenceService.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        KnowledgeGraphPersistenceService.__instance = self

        self.graph = py2neo.Graph(
            env.NEO4J_FACTORY,
            name=cfg.get_str(group=cfg.ConfigGroups.GRAPH, key='database_name')
        )

        self.repo = ogm.Repository(
            env.NEO4J_FACTORY,
            name=cfg.get_str(group=cfg.ConfigGroups.GRAPH, key='database_name')
        )
