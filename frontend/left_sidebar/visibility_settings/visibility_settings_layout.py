import dash_bootstrap_components as dbc

from frontend.left_sidebar.visibility_settings.visibility_settings_enum import GraphVisibilityOptions


def get_layout():
    """
    Layout of the visibility settings
    :return:
    """
    return dbc.Checklist(
        options=[
            {"label": "Show edges", "value": GraphVisibilityOptions.EDGES.value},
            {"label": "Show parts", "value": GraphVisibilityOptions.PARTS.value}
        ],
        value=[GraphVisibilityOptions.EDGES.value],
        id="visibility-switches-input",
        switch=True,
    )

