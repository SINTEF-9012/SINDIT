import dash_bootstrap_components as dbc

from frontend.left_sidebar.global_information import global_information_layout
from frontend.left_sidebar.visibility_settings import visibility_settings_layout


def get_layout():
    """
    Layout of the left sidebar. Contains global information and stats as well as some settings
    :return:
    """
    return dbc.Col(
        children=[
            visibility_settings_layout.get_layout(),
            global_information_layout.get_layout()
        ],
        width=2
    )
