import json

from graph_domain.AssetNode import AssetNodeFlat, AssetNodeDeep
from graph_domain.TimeseriesNode import TimeseriesNodeDeep, TimeseriesNodeFlat
from service.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)
from service.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from service.knowledge_graph.knowledge_graph_metamodel_validator import (
    validate_result_nodes,
)


class TimeseriesDao(object):
    """
    Data Access Object for Timeseries nodes
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

        TimeseriesDao.__instance = self

        self.ps: KnowledgeGraphPersistenceService = (
            KnowledgeGraphPersistenceService.instance()
        )

    @validate_result_nodes
    def get_timeseries_flat(self):
        """
        Queries all timeseries nodes. Does not follow any relationships
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        timeseries_flat_matches = self.ps.repo.match(model=TimeseriesNodeFlat)
        timeseries_flat = [m for m in timeseries_flat_matches]

        return timeseries_flat

    @validate_result_nodes
    def get_timeseries_deep(self):
        """
        Queries all timeseries nodes. Follows relationships to build nested objects for related nodes (e.g. connections)
        :param self:
        :return:
        """
        timeseries_deep_matches = self.ps.repo.match(model=TimeseriesNodeDeep)

        # Get rid of the 'Match' and 'RelatedObject' types in favor of normal lists automatically
        # by using the auto-generated json serializer
        return [
            TimeseriesNodeDeep.from_json(m.to_json()) for m in timeseries_deep_matches
        ]

    # validator used manually because result type is json instead of node-list
    def get_timeseries_deep_json(self):
        """
        Queries all timeseries nodes. Follows relationships to build nested objects for related nodes (e.g. sensors)
        Directly returns the serialized json instead of nested objects. This is faster than using the nested-object
        getter and serializing afterwards, as it does not require an intermediate step.
        :param self:
        :return:
        """
        timeseries_deep_matches = self.ps.repo.match(model=TimeseriesNodeDeep)

        # Validate manually:
        for timeseries in timeseries_deep_matches:
            timeseries.validate_metamodel_conformance()

        return json.dumps([m.to_json() for m in timeseries_deep_matches])
