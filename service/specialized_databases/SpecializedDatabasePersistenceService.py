import abc

from graph_domain.DatabaseConnectionNode import DatabaseConnectionNode
from util.environment_and_configuration import get_environment_variable


class SpecializedDatabasePersistenceService(abc.ABC):
    """
    Persistence service for additional data like files or timeseires
    """

    def __init__(
        self,
        iri,
        database,
        group,
        host_environment_variable,
        port_environment_variable,
        user_environment_variable,
        key_environment_variable,
    ) -> None:
        super().__init__()

        self.iri = iri
        self.database = database
        self.group = group

        self.host = get_environment_variable(
            key=host_environment_variable, optional=False
        )
        self.port = get_environment_variable(
            key=port_environment_variable, optional=False
        )

        self.user = (
            get_environment_variable(
                key=user_environment_variable, optional=True, default=None
            )
            if user_environment_variable is not None
            else None
        )

        self.key = (
            get_environment_variable(
                key=key_environment_variable, optional=True, default=None
            )
            if key_environment_variable is not None
            else None
        )

    @classmethod
    def from_db_connection_node(cls, node: DatabaseConnectionNode):
        return cls(
            iri=node.iri,
            database=node.database,
            group=node.group,
            host_environment_variable=node.host_environment_variable,
            port_environment_variable=node.port_environment_variable,
            user_environment_variable=node.user_environment_variable,
            key_environment_variable=node.key_environment_variable,
        )
