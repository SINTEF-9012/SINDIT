import json

from graph_domain.Machine import MachineFlat, MachineDeep
from service.exceptions.GraphNotConformantToMetamodelError import GraphNotConformantToMetamodelError
from service.knowledge_graph.KnowledgeGraphPersistenceService import KnowledgeGraphPersistenceService
from service.knowledge_graph.knowledge_graph_metamodel_validator import validate_result_node_list


class MachinesDao(object):
    """
    Data Access Object for Machines
    """
    __instance = None

    @staticmethod
    def instance():
        if MachinesDao.__instance is None:
            MachinesDao()
        return MachinesDao.__instance

    def __init__(self):
        if MachinesDao.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        MachinesDao.__instance = self

        self.ps: KnowledgeGraphPersistenceService = KnowledgeGraphPersistenceService.instance()

    @validate_result_node_list
    def get_machines_flat(self):
        """
        Queries all machine nodes. Does not follow any relationships
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        machines_flat_matches = self.ps.repo.match(model=MachineFlat)
        machines_flat = [m for m in machines_flat_matches]

        if not all(machine.validate_metamodel_conformance() for machine in machines_flat):
            raise GraphNotConformantToMetamodelError("Querying the KG did reveal unconsistencies with the metamodel")

        return machines_flat

    @validate_result_node_list
    def get_machines_deep(self):
        """
        Queries all machine nodes. Follows relationships to build nested objects for related nodes (e.g. sensors)
        :param self:
        :return:
        """
        machines_deep_matches = self.ps.repo.match(model=MachineDeep)

        # Get rid of the 'Match' and 'RelatedObject' types in favor of normal lists automatically
        # by using the auto-generated json serializer
        return [MachineDeep.from_json(m.to_json()) for m in machines_deep_matches]

    # validator used manually because result type is json instead of node-list
    def get_machines_deep_json(self):
        """
        Queries all machine nodes. Follows relationships to build nested objects for related nodes (e.g. sensors)
        Directly returns the serialized json instead of nested objects. This is faster than using the nested-object
        getter and serializing afterwards, as it does not require an intermediate step.
        :param self:
        :return:
        """
        machines_deep_matches = self.ps.repo.match(model=MachineDeep)

        if not all(machine.validate_metamodel_conformance() for machine in machines_deep_matches):
            raise GraphNotConformantToMetamodelError("Querying the KG did reveal inconsistencies with the metamodel")

        return json.dumps([m.to_json() for m in machines_deep_matches])
