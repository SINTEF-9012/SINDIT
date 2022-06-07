from dash.dependencies import Input, Output, State

from frontend import api_client
from frontend.app import app
from frontend.right_sidebar.node_data_tab.live_sensor_readings import sensor_readings_layout

sensor_ID = None

print("Initializing sensor callbacks...")


@app.callback(Output('live-update-timeseries', 'figure'),
              Input('interval-component', 'n_intervals'),
              State('cytoscape-graph', 'tapNode'))
def update_live_sensors(n, tap_node):

    # TODO: get id_uri from tap_node
    id_uri = 'www.sintef.no/asset_identifiers/fischertechnik_learning_factory/sensor_inputs/' \
               'HBW/di_PosBelt_Horizontal'

    data = api_client.get_dataframe(f"/sensors/current_timeseries?sensor_id_uri={id_uri}")

    fig = sensor_readings_layout.get_figure()
    fig.add_trace({
        'x': data['time'],
        'y': data['value'],
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)

    return fig
