from typing import List

from graph_domain.BaseNode import BaseNode
from service.exceptions.GraphNotConformantToMetamodelError import GraphNotConformantToMetamodelError


def validate_result_node_list(func):
    """
    Annotation definition for validating KG-query results
    :param func:
    :return:
    """
    def validator_wrapped_getter(*args, **kwargs):
        result_list: List[BaseNode] = func(*args, *kwargs)

        for node in result_list:
            node.validate_metamodel_conformance()

        if not all(node.validate_metamodel_conformance() for node in result_list):
            raise GraphNotConformantToMetamodelError("Querying the KG did reveal inconsistencies with the metamodel")

        return result_list
    return validator_wrapped_getter
