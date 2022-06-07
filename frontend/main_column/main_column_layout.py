import dash_bootstrap_components as dbc

from frontend.main_column.factory_graph import factory_graph_layout


def get_layout():
    """
    Layout of the main column
    :return:
    """

    return dbc.Col(
        children=[
            factory_graph_layout.get_layout(),
        ],
        width=7
    )

