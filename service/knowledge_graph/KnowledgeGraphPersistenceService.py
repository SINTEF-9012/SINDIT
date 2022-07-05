import py2neo
import py2neo.ogm as ogm


from util.environment_and_configuration import get_environment_variable


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
            get_environment_variable(key="NEO4J_DB_HOST", optional=False),
            name=get_environment_variable(key="NEO4J_DB_NAME", optional=False),
        )

        self.repo = ogm.Repository(
            get_environment_variable(key="NEO4J_DB_HOST", optional=False),
            name=get_environment_variable(key="NEO4J_DB_NAME", optional=False),
        )
