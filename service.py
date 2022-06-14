import json

import uvicorn

from service.api.api import app
from service.knowledge_graph.KnowledgeGraphPersistenceService import KnowledgeGraphPersistenceService
from service.knowledge_graph.dao.MachinesDao import MachinesDao
from service.sensor_inputs.ConnectionContainer import ConnectionContainer
from service.timeseries_persistence.TimeseriesPersistenceService import TimeseriesPersistenceService

# Import endpoint files (indirectly used through annotation)

# noinspection PyUnresolvedReferences
from service.api.endpoints import old_endpoints
# noinspection PyUnresolvedReferences
from service.api.endpoints import timeseries_endpoints
# noinspection PyUnresolvedReferences
from service.api.endpoints import graph_endpoints

"""
Main entry point for the application layer
Handles the sensor-connections and provides a API
Introducing services for querying the KG
Separated from api.py to avoid circular dependencies with endpoint files importing the "app" instance. 
"""


# #############################################################################
# Setup sensor connections and timeseries persistence
# #############################################################################
def init_sensors():
    print("Initializing sensor inputs...")

    # Connections
    con_container: ConnectionContainer = ConnectionContainer.instance()
    con_container.initialize_connections()
    con_container.start_connections()

    # Timeseries DB
    TimeseriesPersistenceService.instance()
    con_container.register_persistence_handlers()

    print("Sensor inputs initialized")




# #############################################################################
# Launch services
# #############################################################################
if __name__ == "__main__":
    init_sensors()

    # neo4j tests:
    # m_dao: MachinesDao = MachinesDao.instance()
    # m_json = m_dao.get_machines_deep_json()
    # print(m_json)
    # m_deep = m_dao.get_machines_deep()
    # print(m_deep)
    # m_deep_json = json.dumps([m.to_json() for m in m_deep])
    # print(m_deep_json)
    # m_flat = m_dao.get_machines_flat()
    # print(m_flat)

    # Run fast API
    # noinspection PyTypeChecker
    uvicorn.run(app, host="0.0.0.0", port=8000)
