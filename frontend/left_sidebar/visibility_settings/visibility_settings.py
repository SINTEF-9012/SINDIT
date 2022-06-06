import dash_bootstrap_components as dbc

def get_layout():
    """
    Layout of the visibility settings
    :return:
    """
    return dbc.Checklist(
        options=[
            {"label": "Show edges", "value": 1},
            {"label": "Show parts", "value": 2}
        ],
        value=[1],
        id="switches-input",
        switch=True,
    )

