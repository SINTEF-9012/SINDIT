import json

from graph_domain.AssetNode import AssetNodeFlat, AssetNodeDeep
from service.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)
from service.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from service.knowledge_graph.knowledge_graph_metamodel_validator import (
    validate_result_nodes,
)


class AssetsDao(object):
    """
    Data Access Object for Assets
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

        AssetsDao.__instance = self

        self.ps: KnowledgeGraphPersistenceService = (
            KnowledgeGraphPersistenceService.instance()
        )

    @validate_result_nodes
    def get_assets_flat(self):
        """
        Queries all asset nodes. Does not follow any relationships
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        machines_flat_matches = self.ps.repo.match(model=AssetNodeFlat)
        machines_flat = [m for m in machines_flat_matches]

        return machines_flat

    @validate_result_nodes
    def get_assets_deep(self):
        """
        Queries all asset nodes. Follows relationships to build nested objects for related nodes (e.g. sensors)
        :param self:
        :return:
        """
        machines_deep_matches = self.ps.repo.match(model=AssetNodeDeep)

        # Get rid of the 'Match' and 'RelatedObject' types in favor of normal lists automatically
        # by using the auto-generated json serializer
        return [AssetNodeDeep.from_json(m.to_json()) for m in machines_deep_matches]

    # validator used manually because result type is json instead of node-list
    def get_assets_deep_json(self):
        """
        Queries all asset nodes. Follows relationships to build nested objects for related nodes (e.g. sensors)
        Directly returns the serialized json instead of nested objects. This is faster than using the nested-object
        getter and serializing afterwards, as it does not require an intermediate step.
        :param self:
        :return:
        """
        machines_deep_matches = self.ps.repo.match(model=AssetNodeDeep)

        # Validate manually:
        for machine in machines_deep_matches:
            machine.validate_metamodel_conformance()

        return json.dumps([m.to_json() for m in machines_deep_matches])
