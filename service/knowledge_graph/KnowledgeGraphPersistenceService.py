import py2neo
import py2neo.ogm as ogm

from config import global_config as cfg

import environment.environment as env


class KnowledgeGraphPersistenceService(object):
    """ """

    __instance = None

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls()
        return cls.__instance

    def __init__(self):
        if self.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        KnowledgeGraphPersistenceService.__instance = self

        self.graph = py2neo.Graph(
            env.NEO4J_FACTORY,
            name=cfg.get_str(group=cfg.ConfigGroups.GRAPH, key="database_name"),
        )

        self.repo = ogm.Repository(
            env.NEO4J_FACTORY,
            name=cfg.get_str(group=cfg.ConfigGroups.GRAPH, key="database_name"),
        )
