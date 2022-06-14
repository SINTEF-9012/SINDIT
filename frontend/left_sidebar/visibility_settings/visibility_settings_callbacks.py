from frontend.app import app
from dash.dependencies import Input, Output

from frontend import resources_manager
from frontend.left_sidebar.visibility_settings.visibility_settings_enum import GraphVisibilityOptions

CY_STYLE_STATIC = resources_manager.load_json('cy-style.json')

print("Initializing visibility settings callbacks...")

# @app.callback(Output('cytoscape-graph', 'stylesheet'),
#               Input('visibility-switches-input', 'value'))
# def update_output(value):
#     """
#     Toggles the visibility of element types in the main graph
#     :param value:
#     :return:
#     """
#
#     opacity_edges = 1 if GraphVisibilityOptions.EDGES.value in value else 0
#     opacity_parts = 1 if GraphVisibilityOptions.PARTS.value in value else 0
#
#     additional_styles = [
#         {
#             'selector': 'edge',
#             'style': {
#                 'opacity': opacity_edges
#             }
#         },
#         {
#             "selector": ".SINGLE_PART",
#             'style': {
#                 'opacity': opacity_parts
#             }
#         },
#         {
#             "selector": ".PROCESSED_PART",
#             'style': {
#                 'opacity': opacity_parts
#             }
#         },
#         {
#             "selector": ".part_edge",
#             'style': {
#                 'opacity': opacity_parts
#             }
#         }
#     ]
#
#     return CY_STYLE_STATIC + additional_styles
