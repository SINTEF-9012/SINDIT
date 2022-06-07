import uvicorn

from service.api.api import app
from service.sensor_inputs.ConnectionContainer import ConnectionContainer
from service.timeseries_persistence.TimeseriesPersistenceService import TimeseriesPersistenceService

# Import endpoint files (indirectly used through annotation)

# noinspection PyUnresolvedReferences
from service.api.endpoints import old_endpoints
# noinspection PyUnresolvedReferences
from service.api.endpoints import timeseries_endpoints

"""
Main entry point for the application layer
Handles the sensor-connections and provides a API

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
# Setup fast API
# #############################################################################

def init_api():
    pass
    # noinspection PyTypeChecker
    uvicorn.run(app, host="0.0.0.0", port=8000)


# #############################################################################
# Launch services
# #############################################################################
if __name__ == "__main__":
    init_sensors()
    init_api()
