from app import app
from dash import html
from dash.dependencies import Input, Output
import helper_functions
from frontend import frontend_helpers


print("Initializing navigation callback")

@app.callback(Output('tabs-content', 'children'),
              Input('tabs-infos', 'value'))
def change_navigation_tab(tab):
    """
    Navigation through the tabs of the right sidebar
    :param tab:
    :return:
    """
    # TODO: contents to own files..
    if tab == 'tab-sensors':
        return html.Div([
            helper_functions._draw_time_series_graph(),
            html.Pre(id='cytoscape-tapNodeData', style=frontend_helpers.styles['pre'])
        ])
    elif tab == 'tab-parts':
        return html.Div([
            # helper_functions._draw_parts_graph(parts_cygraph, cystyle),
            # html.Pre(id='cytoscape-tapPartNodeData', style=frontend_helpers.styles['pre'])
        ])
    elif tab == 'tab-nodes':
        return html.Div([
            html.Pre(id='cytoscape-tapNodeData', style=frontend_helpers.styles['pre'])
        ])