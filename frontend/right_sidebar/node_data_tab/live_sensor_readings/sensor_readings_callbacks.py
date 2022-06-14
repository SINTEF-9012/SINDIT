from dash.dependencies import Input, Output, State
import pandas as pd

from frontend import api_client
from config import global_config as cfg
from frontend.app import app
from frontend.right_sidebar.graph_selector import graph_selector_util
from frontend.right_sidebar.node_data_tab.live_sensor_readings import sensor_readings_layout

sensor_ID = None

LIVE_SENSOR_DISPLAY_DURATION = cfg.get_float(
                group=cfg.ConfigGroups.FRONTEND,
                key='current_timeseries_duration')

print("Initializing sensor callbacks...")


@app.callback(Output('live-update-timeseries', 'figure'),
              Input('interval-component', 'n_intervals'),
              State('selected-graph-element-store', 'data'))
def update_live_sensors(n, selected_el):

    if graph_selector_util.get_type(selected_el) == graph_selector_util.SelectedElementTypes.TIMESERIES_INPUT:
        id_uri = graph_selector_util.get_iri(selected_el)
        data = api_client.get_dataframe(f"/timeseries/current_measurements"
                                        f"?id_uri={id_uri}"
                                        f"&duration={LIVE_SENSOR_DISPLAY_DURATION}")
    else:
        print("Trying to visualize timeseries from non-timeseries element...")
        data = pd.DataFrame(columns=['time', 'value'])

    fig = sensor_readings_layout.get_figure()
    fig.add_trace({
        'x': data['time'],
        'y': data['value'],
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)

    return fig
