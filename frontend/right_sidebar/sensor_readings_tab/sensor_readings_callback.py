from app import app

from dash.dependencies import Input, Output, State
import requests
import plotly
import environment.settings as stngs
import helper_functions

API_URI = stngs.FAST_API_URI
sensor_ID = None

print("Initializing sensor callback")

@app.callback(Output('live-update-timeseries', 'figure'),
              Input('interval-component', 'n_intervals'),
              State('cytoscape-graph', 'tapNode'))
def update_live_sensors(n, data):
    data = {
        'time': [],
        'value': [],
        'type': 'na'
    }

    print('update_live_sensors: sensor_ID ' + str(sensor_ID))
    if sensor_ID != None:
        sensor_info = requests.get(API_URI + '/get_sensor_info/' + str(sensor_ID)).json()

        r = helper_functions._generate_sensor_data(duration_h=3)

        data['type'] = sensor_info['type']

        for entry in r:
            data['value'].append(entry['value'])
            data['time'].append(entry['timestamp'])

    # Create the graph with subplots
    fig = plotly.tools.make_subplots(rows=1, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.append_trace({
        'x': data['time'],
        'y': data['value'],
        'name': data['type'],
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)

    return fig