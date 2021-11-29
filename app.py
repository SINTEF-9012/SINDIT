"""
Client for Digital Shadow.

Author: Maryna Waszak <maryna.waszak@sintef.no>
"""

import dash
import dash_cytoscape as cyto
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import requests
import json
import datetime
import plotly
import pandas as pd
import numpy as np
import environment.settings as stngs
import random

API_URI = stngs.FAST_API_URI
sensor_ID = None
# #############################################################################
# #############################################################################
# #############################################################################
# HELPER FUNCTIONS
# #############################################################################
# #############################################################################
# #############################################################################
def _generate_sensor_data(duration_h=3):
    
    date_rng = pd.date_range(start=pd.Timestamp(datetime.datetime.now()-datetime.timedelta(hours=duration_h)), end=pd.Timestamp(datetime.datetime.now()), freq='1T')  
        
    df = pd.DataFrame(date_rng, columns=['time_ms'])   
    df['data 0'] = np.random.randint(0,50,size=(len(date_rng)))
    df['data 1'] = np.random.randint(0,100,size=(len(date_rng)))
        
    time_ms_array = np.zeros(len(date_rng))
    for index, row in df.iterrows():  
        time_ms_array[index] = int(row['time_ms'].timestamp()*1000)
    
    df['data 2'] = np.sin(time_ms_array)*70
    df['data 3'] = np.random.randint(0,100,size=(len(date_rng)))+np.sin(time_ms_array)*5

    sensor_readings = pd.DataFrame(data={'value': df['data '+ str(random.randint(0,3))].to_numpy().tolist(), \
                                'timestamp': pd.to_datetime(time_ms_array, unit='ms')})

    return json.loads(sensor_readings.to_json(orient="records"))

def _load_json(st):
    if 'http' in st:
        return requests.get(st).json()
    else:
        if st[0] == '/': st = st[1:]
        # print(st)
        with open(st, 'rb') as f:
            x = json.load(f)
        return x
    
def _draw_table_part_infos(data):
    header_style={'color': 'black', 'fontSize': 14, 'font-weight':'bold'}
    rows = []    
    if data:
        rows.append(html.Tr([html.Td(data['data']['type'], style=header_style), html.Td(data['data']['id'])]))
        rows.append(html.Tr([html.Td('Description:'), html.Td(data['data']['label'])]))
                
    table_body = [html.Tbody(rows)]
    table = dbc.Table(table_body, id='part_node_info-text', bordered=False)

    return table

def _draw_table_node_infos(data):
    header_style={'color': 'black', 'fontSize': 14, 'font-weight':'bold'}
    rows = []    
    if data:
        print(data['data']['id']+': '+str(data['position']['x'])+'/'+str(data['position']['y']))              
        if data['data']['type']=='BUFFER' or data['data']['type']=='CONTAINER':
            rows.append(html.Tr([html.Td(data['data']['type'], style=header_style), html.Td(data['data']['id'])]))
            rows.append(html.Tr([html.Td('Description:'), html.Td(data['data']['label'])]))
            amount = requests.get(API_URI+'/get_amount_on_queue/'+data['data']['id']).json()
            rows.append(html.Tr([html.Td('Amount:'), html.Td(amount)]))
        elif data['classes'] == 'SENSOR':
            global sensor_ID
            sensor_ID = data['data']['id']
            rows.append(html.Tr([html.Td(data['classes'], style=header_style), html.Td(data['data']['id'])]))
            rows.append(html.Tr([html.Td('Description:'), html.Td(data['data']['label'])]))
            rows.append(html.Tr([html.Td('Type:'), html.Td(data['data']['type'])]))
        else:
            rows.append(html.Tr([html.Td(data['data']['type'], style=header_style), html.Td(data['data']['id'])]))
            rows.append(html.Tr([html.Td('Description:'), html.Td(data['data']['label'])]))
            
    
    table_body = [html.Tbody(rows)]
    table = dbc.Table(table_body, id='node_info-text', bordered=False)

    return table

def _draw_table():
    time_now = datetime.datetime.now()
    shift_end = time_now.replace(hour=19, minute=30)
    remaining_work_time = (shift_end-time_now)
    if remaining_work_time.total_seconds() < 0:
        remaining_work_time = datetime.timedelta(0)
    def reformat_delta_time(delta):
        ms = delta.microseconds//1000
        sec = delta.seconds
        hours = sec // 3600
        minutes = (sec // 60) - (hours * 60)   
        seconds = sec - (minutes*60) - (hours * 60)
        new_format = str(hours)+' h '+str(minutes) +' min'
        if hours == 0 and minutes == 0:
            new_format = str(seconds)+' sec'
        if sec == 0:
            new_format = str(ms)+' msec'
        return new_format
    rows = []     
    header_style={'color': 'black', 'fontSize': 14, 'font-weight':'bold'}
    rows.append(html.Tr([html.Td("TIMES [hh:mm]", style=header_style), html.Td()]))
    rows.append(html.Tr([html.Td("Current Time"), html.Td(time_now.strftime("%H:%M"))]))
    rows.append(html.Tr([html.Td("Shift ends at"), html.Td(shift_end.strftime("%H:%M"))]) )      
    rows.append(html.Tr([html.Td("Remaining time"), html.Td(reformat_delta_time(remaining_work_time))]))
    rows.append(html.Tr([html.Td(), html.Td()]))
    
    # we know that P10.1 is the last process in the production before the exit node
    #@todo: look for the specific process before the exit buffers
    last_arr_time = requests.get(API_URI+'/get_last_prod_arrival_time_from_influxDB/'+'P10.1').json()    
    avg_arr_time = requests.get(API_URI+'/get_avg_arrival_freq_from_influxDB/'+'P10.1').json()
    rows.append(html.Tr([html.Td("PARTS ARRIVAL [hh:mm]", style=header_style), html.Td()]))
    avg_arr_time_str = 'not available'
    last_arr_time_str = 'not available'
    if not isinstance(avg_arr_time, str):
        avg_arr_time = datetime.timedelta(milliseconds = avg_arr_time)  
        avg_arr_time_str = reformat_delta_time(avg_arr_time)   
        last_arr_time_str = last_arr_time

    rows.append(html.Tr([html.Td("Avg. arrival duration"), html.Td(avg_arr_time_str)]))
    rows.append(html.Tr([html.Td("Last product arrived at"), html.Td(last_arr_time_str)]))
    rows.append(html.Tr([html.Td(), html.Td()]))
         
    parts = requests.get(API_URI+'/get_exit_parts/').json() 
    planned_amount = 150
    rows.append(html.Tr([html.Td("TOTAL AMOUNT [pieces]", style=header_style), html.Td()]))
    rows.append(html.Tr([html.Td("Planned amount"), html.Td(planned_amount)]))
    rows.append(html.Tr([html.Td("Ammount left on remaining time"), html.Td(planned_amount-len(parts))]))
    rows.append(html.Tr([html.Td(), html.Td()]))
    
    # constantly run a fast simulation to do this estimate
    sim_time = int(remaining_work_time.total_seconds())   
    response = None#requests.get(API_URI+'/get_sim_prediction_from_neo4j/'+str(sim_time))
    try:
        sim_results = response.json() 
        parts_est = sim_results[0]['num_of_parts'] 
    except:
        parts_est = 'not available'
    rows.append(html.Tr([html.Td("ESTIMATED AMOUNT BY SHIFT END", style=header_style), html.Td(parts_est)]))
    rows.append(html.Tr([html.Td(), html.Td()]))
       
    rows.append(html.Tr([html.Td("CURRENT AMOUNT", style=header_style), html.Td(len(parts))]))
    table_body = [html.Tbody(rows)]

    table = dbc.Table(table_body, id='live-update-table-text', bordered=False)

    return table

def _draw_parts_graph(parts_cygraph,cystyle):
  
    cyto_card_graph = cyto.Cytoscape(
                    id='cytoscape-parts-graph',
                    layout={'name': 'cose'},
                    style={'width': '100%', 'height': '200px'},
                    stylesheet=cystyle,
                    elements=parts_cygraph)
        
    return html.Div([
        dbc.Card([
            dbc.CardHeader("Parts graph"),
            dbc.CardBody([cyto_card_graph]),                
        ]),
    ])

def _draw_switch():
    return dbc.Form([
            dbc.Checklist(
                options=[
                    {"label": "Show edges", "value": 1},
                    {"label": "Show parts", "value": 2}
                ],
                value=[1],
                id="switches-input",
                switch=True,
            ),      
    ])

def _draw_time_series_graph():
    graph = html.Div(children=[
            html.Td('Real-time data from sensors'),
            dcc.Graph(id='live-update-timeseries'),
            ])
    return graph

# #############################################################################
# #############################################################################
# #############################################################################
# BUILD AND INIT WEBAPP
# #############################################################################
# #############################################################################
# #############################################################################

# Build App
external_stylesheets = [dbc.themes.SPACELAB]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Load Data
cystyle = _load_json(app.get_asset_url('cy-style.json'))
cygraph = requests.get(API_URI+'/get_factory_cytoscape_from_neo4j').json()
parts_cygraph = []
graph_name = requests.get(API_URI+'/get_factory_name').json()

GRAPH_CARD_STYLE={}#{'background-image': ['url('+BACKGROUND_IMAGE+')'],
                   # 'background-repeat': 'no-repeat',
                   # 'background-position': '1200px 55px',
                   # 'background-size': '400px 100px'}

def _draw_graph(cygraph,cystyle):
    return html.Div([
        dbc.Card([
            dbc.CardHeader("Factory graph"),
            dbc.CardBody([
                cyto.Cytoscape(
                    id='cytoscape-graph',
                    layout={'name': 'preset'},
                    style={'width': '100%', 'height': '770px'},
                    stylesheet=cystyle,
                    elements=cygraph)
            ],style=GRAPH_CARD_STYLE)
        ]),
    ])
# Layout
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
SINTEF_LOGO = app.get_asset_url('sintef_blue.png')

app.layout = html.Div([
    dbc.Navbar(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=SINTEF_LOGO, height="32px")),
                        # dbc.Col(dbc.NavbarBrand("SINDIT", className="ml-2")),
                    ],
                    align="center"
                ),
                href="https://www.sintef.no"
            ),
        ]
    ),
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    _draw_switch(),                     
                    _draw_table()
                ], width=2),
                dbc.Col([
                    _draw_graph(cygraph, cystyle),
                    html.Div(children=[dcc.Input(id='input-on-submit', type='number', value=40), 'Simulation duration']),
                    html.Div(children=[dcc.Input(id='parts-on-submit', type='number', value=10), 'Add amount on source']),
                    html.Button('Simulate', id='submit-val', n_clicks=0),
                    html.Button('Reset', id='reset-val', n_clicks=0),
                    html.Div(id='run_event_sim_button',children='Enter a simulation duration'),
                ], width=8),
                dbc.Col([
                    dcc.Tabs(id='tabs-infos', value='tab-nodes', children=[
                    dcc.Tab(label='More information', value='tab-nodes'),
                    dcc.Tab(label='Parts history', value='tab-parts'),
                    dcc.Tab(label='Sensors time-series', value='tab-sensors')
                    ]),
                    html.Div(id='tabs-content')
                ], width=2),
                dcc.Interval(
                    id='interval-component',
                    interval=5000, # in milliseconds
                    n_intervals=0)
            ], align='start'),
        ])
    )
])

     
# #############################################################################
# #############################################################################
# #############################################################################
# CALLBACKS
# #############################################################################
# #############################################################################
# #############################################################################
@app.callback(Output('tabs-content', 'children'),
              Input('tabs-infos', 'value'))
def render_content(tab):
    if tab == 'tab-sensors':
        return html.Div([
            _draw_time_series_graph(),
            html.Pre(id='cytoscape-tapNodeData', style=styles['pre'])
        ])
    elif tab == 'tab-parts':
        return html.Div([
            _draw_parts_graph(parts_cygraph, cystyle),
             html.Pre(id='cytoscape-tapPartNodeData', style=styles['pre'])
        ])
    elif tab == 'tab-nodes':
        return html.Div([
            html.Pre(id='cytoscape-tapNodeData', style=styles['pre'])
        ])

@app.callback(Output('cytoscape-tapPartNodeData', 'children'),
              Input('cytoscape-parts-graph', 'tapNode'))
def displayTapPartHistNodeData(data):             
    return _draw_table_part_infos(data)

@app.callback(Output('live-update-table-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_date(n):
      return _draw_table()
  
@app.callback(Output('cytoscape-graph', 'elements'),
              Input('interval-component', 'n_intervals'))
def update_factory_graph(n):
    cygraph = requests.get(API_URI+'/get_factory_cytoscape_from_neo4j').json()
    return cygraph
                   
@app.callback(Output('live-update-timeseries', 'figure'),
              Input('interval-component', 'n_intervals'),
              State('cytoscape-graph', 'tapNode'))
def update_live_sensors(n, data):
    data = {
        'time': [],
        'value': [],
        'type': 'na'
    }   

    print('update_live_sensors: sensor_ID '+str(sensor_ID))
    if sensor_ID != None: 
        sensor_info = requests.get(API_URI+'/get_sensor_info/'+str(sensor_ID)).json()
            
        r = _generate_sensor_data(duration_h = 3)

        data['type']=sensor_info['type']
        
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

@app.callback(Output('cytoscape-tapNodeData', 'children'),
              Input('cytoscape-graph', 'tapNode'),
              State('tabs-infos', 'value'),
              prevent_initial_call=True)
def displayTapNodeData(data, tab_name):
    if data['classes'] != 'SENSOR' and tab_name == 'tab-sensors': 
        return None 

    return _draw_table_node_infos(data)


@app.callback(Output('cytoscape-parts-graph', 'elements'),
              Input('cytoscape-graph', 'tapNode'))
def displayTapPartNodeData(data):
    parts_cygraph = []
    if data:
        print(data['data']['id'])
        if data['data']['type']=='SINGLE_PART' or data['data']['type']=='PROCESSED_PART':
            uuid = data['data']['id']
            parts_cygraph = requests.get(API_URI+'/get_part_cytoscape_from_neo4j/'+uuid).json()

    return parts_cygraph 
   
@app.callback(Output('run_event_sim_button', 'children'),
              Input('reset-val', 'n_clicks'),
              Input('submit-val', 'n_clicks'),    
              State('input-on-submit', 'value'),
              State('parts-on-submit', 'value'),
              prevent_initial_call=True)
def run_event_sim(reset, submit, value_duration, num_entry_amount): 
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-val' in changed_id:
        print('Reset was triggered')
        file_path = '../*.json'
        request = API_URI+'/push_json_factory_and_parts_to_neo4j/'+file_path
        requests.post(request)
        return 'Reset is done, you can start simulation again.'
    else:      
        print('Descrete event simulation was triggered for ', value_duration, ' seconds and ', num_entry_amount, ' added amount/parts')
        sim_request = API_URI+'/run_factory/'+str(value_duration)+'/'+str(num_entry_amount)
        sim_results = requests.get(sim_request) 
        try:
            sim_results_json =  sim_results.json() 
            result_string = ' {} parts'.format(sim_results_json[0]['amount'])   
        except: 
            result_string = json.dumps(sim_results)

        return result_string
    
             

@app.callback(Output('cytoscape-graph', 'stylesheet'),
              Input('switches-input', 'value'))
def update_output(value):
    opacity_edges = 0
    opacity_parts = 0
    if 1 in value:
        opacity_edges = 1
    if 2 in value:
        opacity_parts = 1
    new_styles = [
        {
            'selector': 'edge',
            'style': {
                'opacity': opacity_edges
            }
        },
        {
            "selector": ".SINGLE_PART",
            'style': {
                'opacity': opacity_parts
            }
        },
        {
            "selector": ".PROCESSED_PART",
            'style': {
                'opacity': opacity_parts
            }
        },
        {
            "selector": ".part_edge",
            'style': {
                'opacity': opacity_parts
            }
        }
    ]
    print(value)
    return cystyle + new_styles

         
# Launch App
app.run_server(host='0.0.0.0',debug=False, port=8050)
