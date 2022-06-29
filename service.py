import json

import uvicorn

from service.api.api import app
from service.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from service.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from service.sensor_inputs.ConnectionContainer import ConnectionContainer
from service.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from service.specialized_databases.timeseries.influx_db.InfluxDbPersistenceService import (
    InfluxDbPersistenceService,
)

# Import endpoint files (indirectly used through annotation)

# noinspection PyUnresolvedReferences
from service.api.endpoints import old_endpoints

# noinspection PyUnresolvedReferences
from service.api.endpoints import timeseries_endpoints

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
    print("Initializing Knowledge Graph...")

    kg_service: KnowledgeGraphPersistenceService = (
        KnowledgeGraphPersistenceService.instance()
    )
    db_con_nodes_dao: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()

    print("Initializing database connections...")

    db_con_container: DatabasePersistenceServiceContainer = (
        DatabasePersistenceServiceContainer.instance()
    )

    db_con_nodes = db_con_nodes_dao.get_database_connections()

    db_con_container.initialize_connections(db_con_nodes)


def init_sensors():
    print("Initializing sensor inputs...")

    # Connections
    con_container: ConnectionContainer = ConnectionContainer.instance()
    con_container.initialize_connections()
    con_container.start_connections()

    # Timeseries DB
    InfluxDbPersistenceService.instance()
    con_container.register_persistence_handlers()

    print("Sensor inputs initialized")


# #############################################################################
# Launch services
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
