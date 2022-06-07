import dash
import dash_bootstrap_components as dbc

"""
Plotly dash app instance.
Separated from frontend.py to avoid circular dependencies with callback files importing the "app" instance. 
"""

# Build App
external_stylesheets = [dbc.themes.SPACELAB]
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    assets_folder="../assets"
)
