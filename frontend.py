from frontend.app import app
from frontend import page_layout

from sensor_inputs.ConnectionContainer import ConnectionContainer
from timeseries_persistence.TimeseriesPersistenceService import TimeseriesPersistenceService

# Import callback files (indirectly used through annotation)

# noinspection PyUnresolvedReferences
from frontend.right_sidebar.node_data_tab.live_sensor_readings import sensor_readings_callbacks
# noinspection PyUnresolvedReferences
from frontend.right_sidebar import navigation_callbacks
# noinspection PyUnresolvedReferences
from frontend.left_sidebar.visibility_settings import visibility_settings_callbacks
# noinspection PyUnresolvedReferences
from frontend.left_sidebar.global_information import global_information_callbacks
# noinspection PyUnresolvedReferences
from frontend.main_column.factory_graph import factory_graph_callbacks

"""
Main entry point
Separated from app.py to avoid circular dependencies with callback files importing the "app" instance. 
"""

def init_dash_app():
    # Initialize layout
    app.layout = page_layout.get_layout()

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
# Launch frontend
# #############################################################################
if __name__ == "__main__":
    init_dash_app()

    init_sensors()
    app.run_server(host='0.0.0.0', debug=False, port=8050, use_reloader=False)
