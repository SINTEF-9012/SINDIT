import dash_bootstrap_components as dbc

from frontend.left_sidebar.global_information import global_information
from frontend.left_sidebar.visibility_settings import visibility_settings


def get_layout():
    """
    Layout of the left sidebar. Contains global information and stats as well as some settings
    :return:
    """
    return dbc.Col([
        visibility_settings.get_layout(),
        global_information.get_layout()
    ], width=2)
