
from app import app
from frontend import page

from sensor_inputs.ConnectionContainer import ConnectionContainer
from timeseries_persistence.TimeseriesPersistenceService import TimeseriesPersistenceService

from dash.dependencies import Input, Output, State
import requests
import environment.settings as stngs
import helper_functions
import dash
import json

# Import callback files (indirectly used through annotation)

# noinspection PyUnresolvedReferences
from frontend.right_sidebar.sensor_readings_tab import sensor_readings_callback
# noinspection PyUnresolvedReferences
from frontend.right_sidebar import navigation_callbacks

# noinspection PyUnresolvedReferences
from frontend.left_sidebar.visibility_settings import visibility_settings_callbacks

"""
Main entry point
Separated from app.py to avoid circular dependencies with callback files importing the "app" instance. 
"""

# @app.callback(Output('run_event_sim_button', 'children'),
#               Input('reset-val', 'n_clicks'),
#               Input('submit-val', 'n_clicks'),
#               State('input-on-submit', 'value'),
#               prevent_initial_call=True)
# def run_event_sim(reset, submit, value_duration):
#     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
#     if 'reset-val' in changed_id:
#         print('Reset was triggered')
#         file_path = 'chocolate_factory.json'
#         request = API_URI + '/push_json_factory_and_parts_to_neo4j/' + file_path
#         requests.post(request)
#         return 'Reset is done, you can start simulation again.'
#     else:
#         print('Descrete event simulation was triggered')
#         num_entry_amount = 0
#         sim_request = API_URI + '/run_factory/' + str(value_duration) + '/' + str(num_entry_amount)
#         sim_results = requests.get(sim_request)
#         try:
#             sim_results_json = sim_results.json()
#             result_string = ' {} parts'.format(sim_results_json[0]['amount'])
#         except:
#             result_string = json.dumps(sim_results)
#
#         return result_string

def init_dash_app():
    # Initialize layout
    app.layout = page.get_layout()

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
    ts_service = TimeseriesPersistenceService.instance()
    con_container.register_persistence_handlers()

    print("Sensor inputs initialized")


# #############################################################################
# Launch frontend
# #############################################################################
if __name__ == "__main__":
    print("a")
    init_dash_app()

    init_sensors()
    app.run_server(host='0.0.0.0', debug=False, port=8050, use_reloader=False)
