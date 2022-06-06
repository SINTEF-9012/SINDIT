from app import app
from dash.dependencies import Input, Output

from frontend.left_sidebar.global_information import global_information


@app.callback(Output('live-update-table-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_date(n):
    """
    Periodically refreshes the global information
    :param value:
    :return:
    """
    return global_information.get_layout()
