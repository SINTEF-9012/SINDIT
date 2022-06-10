from frontend.app import app
from dash.dependencies import Input, Output

from frontend.left_sidebar.global_information import global_information_layout

print("Initializing global information callbacks...")

@app.callback(Output('global-information-container', 'children'),
              Input('interval-component', 'n_intervals'))
def update_global_information(n):
    """
    Periodically refreshes the global information
    :param n:
    :return:
    """
    return global_information_layout.get_content()
