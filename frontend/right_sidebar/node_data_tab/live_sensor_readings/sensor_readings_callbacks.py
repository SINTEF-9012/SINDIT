from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State

from config import global_config as cfg
from frontend.app import app
from frontend.right_sidebar.node_data_tab.live_sensor_readings import sensor_readings_layout
from service.timeseries_persistence.TimeseriesPersistenceService import TimeseriesPersistenceService

sensor_ID = None

print("Initializing sensor callbacks...")


@app.callback(Output('live-update-timeseries', 'figure'),
              Input('interval-component', 'n_intervals'),
              State('cytoscape-graph', 'tapNode'))
def update_live_sensors(n, tap_node):

    # TODO: get id_uri from tap_node

    # TODO: api instead of direct access
    ts_service: TimeseriesPersistenceService = TimeseriesPersistenceService.instance()

    data = ts_service.read_period_to_dataframe(
        id_uri='www.sintef.no/asset_identifiers/fischertechnik_learning_factory/sensor_inputs/' \
               'HBW/di_PosBelt_Horizontal',
        begin_time=datetime.now() - timedelta(seconds=cfg.get_int(
            group=cfg.ConfigGroups.FRONTEND,
            key='sensor_data_display_duration')),
        end_time=datetime.now()
    )

    fig = sensor_readings_layout.get_figure()

    fig.add_trace({
        'x': data['time'],
        'y': data['value'],
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)

    return fig
