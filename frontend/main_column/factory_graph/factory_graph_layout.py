from typing import List

from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from frontend.app import app
from frontend import resources_manager
from graph_domain.BaseNode import BaseNode
from graph_domain.DatabaseConnection import DatabaseConnection
from graph_domain.Machine import MachineDeep
from graph_domain.Timeseries import TimeseriesDeep
from graph_domain.Unit import Unit
from graph_domain.factory_graph_types import (
    UNSPECIFIED_LABEL,
    NodeTypes,
    RelationshipTypes,
)

CY_GRAPH_STYLE_STATIC = resources_manager.load_json("cytoscape-graph-style.json")


def get_layout():
    return html.Div(
        [
            # Storage for accessing the selected element
            dcc.Store(id="selected-graph-element-store"),
            # Timestamp for the selected element storage
            dcc.Store(id="selected-graph-element-timestamp"),
            dbc.Card(
                [
                    dbc.CardHeader("Factory graph"),
                    dbc.CardBody(
                        html.Div(
                            id="kg-container",
                            children=[
                                cyto.Cytoscape(
                                    id="cytoscape-graph",
                                    layout={"name": "preset"},
                                    style={"width": "100%", "height": "75vh"},
                                    stylesheet=CY_GRAPH_STYLE_STATIC,
                                    className="factory-graph",
                                )
                            ],
                        )
                    ),
                    dbc.CardFooter(
                        id="graph-positioning-container",
                        style={"display": "None"},
                        children=[
                            dbc.Row(
                                children=[
                                    dbc.Col(
                                        dbc.Button(
                                            "Save node position",
                                            id="graph-positioning-save-button",
                                            n_clicks=0,
                                        ),
                                        style={"height": "100%"},
                                    ),
                                    dbc.Col(
                                        children=[
                                            dbc.Alert(
                                                id="graph-positioning-saved-notifier",
                                                class_name="inline-alert",
                                                is_open=False,
                                                duration=5000,
                                            )
                                        ],
                                        style={"height": "100%"},
                                    ),
                                ],
                                style={"height": "40px"},
                            )
                        ],
                    ),
                ]
            ),
        ]
    )


def _create_cytoscape_node(node: BaseNode, node_type: str = UNSPECIFIED_LABEL):
    # Restore node positioning where available:
    pox_x = (
        node.visualization_positioning_x
        if node.visualization_positioning_x is not None
        else 0
    )
    pox_y = (
        node.visualization_positioning_y
        if node.visualization_positioning_y is not None
        else 0
    )

    return {
        "data": {
            "id": node.id_short,
            "label": node.id_short,
            "type": node_type,
            "iri": node.iri,
            "description": node.description,
        },
        "classes": [node_type],
        "position": {"x": pox_x, "y": pox_y},
    }


def _create_cytoscape_relationship(
    node_from: BaseNode, node_to: BaseNode, edge_type: str = UNSPECIFIED_LABEL
):
    return {
        "data": {
            "source": node_from.id_short,
            "target": node_to.id_short,
        },
        "classes": [edge_type],
    }


def get_cytoscape_elements(machines_deep: List[MachineDeep]):
    cytoscape_elements = []

    for machine in machines_deep:
        # Machines:
        cytoscape_elements.append(
            _create_cytoscape_node(machine, NodeTypes.MACHINE.value)
        )

        for timeseries in machine.timeseries:
            # Timeseries:
            cytoscape_elements.append(
                _create_cytoscape_node(timeseries, NodeTypes.TIMESERIES_INPUT.value)
            )
            cytoscape_elements.append(
                _create_cytoscape_relationship(
                    machine, timeseries, RelationshipTypes.HAS_TIMESERIES.value
                )
            )

            # Database connection:
            cytoscape_elements.append(
                _create_cytoscape_node(
                    timeseries.connection, NodeTypes.DATABASE_CONNECTION.value
                )
            )
            cytoscape_elements.append(
                _create_cytoscape_relationship(
                    timeseries, timeseries.connection, RelationshipTypes.DB_ACCESS.value
                )
            )

            # Unit:
            cytoscape_elements.append(
                _create_cytoscape_node(timeseries.unit, NodeTypes.UNIT.value)
            )
            cytoscape_elements.append(
                _create_cytoscape_relationship(
                    timeseries, timeseries.unit, RelationshipTypes.HAS_UNIT.value
                )
            )

    return cytoscape_elements
