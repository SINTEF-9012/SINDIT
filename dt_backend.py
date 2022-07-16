import json

import uvicorn

from service.api.api import app
from service.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from service.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from service.knowledge_graph.dao.TimeseriesNodesDao import TimeseriesDao
from service.runtime_connections.RuntimeConnectionContainer import (
    RuntimeConnectionContainer,
)
from service.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from service.specialized_databases.timeseries.influx_db.InfluxDbPersistenceService import (
    InfluxDbPersistenceService,
)

# Import endpoint files (indirectly used through annotation)

# noinspection PyUnresolvedReferences
from service.api.endpoints import timeseries_endpoints

# noinspection PyUnresolvedReferences
from service.api.endpoints import file_endpoints

# noinspection PyUnresolvedReferences
from service.api.endpoints import asset_endpoints

# noinspection PyUnresolvedReferences
from service.api.endpoints import graph_endpoints
from util.environment_and_configuration import (
    get_environment_variable,
    get_environment_variable_int,
)

"""
Main entry point for the application layer
Handles the sensor-connections and provides a API
Introducing services for querying the KG
Separated from api.py to avoid circular dependencies with endpoint files importing the "app" instance. 
"""


# #############################################################################
# Setup sensor connections and timeseries persistence
# #############################################################################
def init_database_connections():
    print("Initializing database connections...")

    kg_service: KnowledgeGraphPersistenceService = (
        KnowledgeGraphPersistenceService.instance()
    )
    db_con_nodes_dao: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()

    db_con_container: DatabasePersistenceServiceContainer = (
        DatabasePersistenceServiceContainer.instance()
    )

    db_con_nodes = db_con_nodes_dao.get_database_connections()

    db_con_container.initialize_connections(db_con_nodes)

    print("Done!")


def init_sensors():
    print("Initializing timeseries inputs...")

    kg_service: KnowledgeGraphPersistenceService = (
        KnowledgeGraphPersistenceService.instance()
    )
    timeseries_nodes_dao: TimeseriesDao = TimeseriesDao.instance()

    runtime_con_container: RuntimeConnectionContainer = (
        RuntimeConnectionContainer.instance()
    )

    timeseries_deep_nodes = timeseries_nodes_dao.get_timeseries_deep()

    runtime_con_container.initialize_connections_inputs_and_handlers(
        timeseries_deep_nodes
    )

    runtime_con_container.start_connections()

    print("Done!")


# #############################################################################
# Launch backend
# #############################################################################
if __name__ == "__main__":
    init_database_connections()
    init_sensors()

    # Run fast API
    # noinspection PyTypeChecker
    uvicorn.run(
        app,
        host=get_environment_variable("FAST_API_HOST"),
        port=get_environment_variable_int("FAST_API_PORT"),
    )
