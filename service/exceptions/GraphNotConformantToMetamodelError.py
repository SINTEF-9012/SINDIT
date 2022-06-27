
class GraphNotConformantToMetamodelError(Exception):
    """The KG is not conformant to the metamodel! This should never happen"""
    def __init__(self, node, problem_str: str) -> None:
        super().__init__(f"Querying the KG did reveal inconsistencies with the metamodel!\nProblem: {problem_str}\nNode: ID_short: {node.id_short},\niri: {node.iri}")
