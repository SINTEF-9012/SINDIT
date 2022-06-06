"""
Client for Digital Shadow.

Author: Maryna Waszak <maryna.waszak@sintef.no>
"""

import dash
import dash_bootstrap_components as dbc
# import requests
# import environment.settings as stngs

# import helper_functions
# from frontend import page

# API_URI = stngs.FAST_API_URI
# sensor_ID = None



# #############################################################################
# BUILD AND INIT WEBAPP
# #############################################################################


# Build App
external_stylesheets = [dbc.themes.SPACELAB]
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True
)

# Load Data
# cystyle = helper_functions._load_json(app.get_asset_url('cy-style.json'))
# cygraph = requests.get(API_URI + '/get_factory_cytoscape_from_neo4j').json()
# parts_cygraph = []
# graph_name = requests.get(API_URI + '/get_factory_name').json()
#
#
# SINTEF_LOGO = app.get_asset_url('sintef_blue.png')

# # Initialize layout
# app.layout = page.get_layout()








