import dash_bootstrap_components as dbc
from dash import html, dcc

from graph_domain.factory_graph_types import NodeTypes


def get_layout():
    """
    Layout of the visibility settings
    :return:
    """
    return html.Div(
        [
            dbc.Checklist(
                options=[
                    {"label": "Show machines", "value": NodeTypes.MACHINE.value},
                    {
                        "label": "Show timeseries inputs",
                        "value": NodeTypes.TIMESERIES_INPUT.value,
                    },
                    {
                        "label": "Show database connections",
                        "value": NodeTypes.DATABASE_CONNECTION.value,
                    },
                    {
                        "label": "Show runtime connections",
                        "value": NodeTypes.RUNTIME_CONNECTION.value,
                    },
                    {"label": "Show units", "value": NodeTypes.UNIT.value},
                ],
                value=[NodeTypes.MACHINE.value, NodeTypes.TIMESERIES_INPUT.value],
                id="visibility-switches-input",
                switch=True,
            )
        ]
    )
