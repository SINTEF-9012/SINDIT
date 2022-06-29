from typing import List

from graph_domain.BaseNode import BaseNode
from service.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)


def validate_result_nodes(func):
    """
    Annotation definition for validating KG-query results
    :param func:
    :return:
    """

    def validator_wrapped_getter(*args, **kwargs):
        result = func(*args, *kwargs)

        if isinstance(result, list):
            node: BaseNode
            for node in result:
                node.validate_metamodel_conformance()
        elif isinstance(result, BaseNode):
            result.validate_metamodel_conformance()

        # None as result is accepted by this validation

        return result

    return validator_wrapped_getter
