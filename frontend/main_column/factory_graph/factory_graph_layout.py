from typing import List

from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from frontend.app import app
from frontend import resources_manager
from frontend.main_column.factory_graph.factory_graph_types import SelectedElementTypes
from graph_domain.BaseNode import BaseNode
from graph_domain.Machine import MachineDeep
from graph_domain.Timeseries import TimeseriesDeep

CY_STYLE_STATIC = resources_manager.load_json('cy-style.json')


def get_layout():
    return html.Div(
        [
            # Storage for accessing the selected element
            dcc.Store(id='selected-graph-element-store'),
            # Timestamp for the selected element storage
            dcc.Store(id='selected-graph-element-timestamp'),

            dbc.Card([
                dbc.CardHeader("Factory graph"),
                dbc.CardBody(
                    html.Div(
                        id="kg-container",
                        children=[
                            cyto.Cytoscape(
                                id='cytoscape-graph',
                                layout={'name': 'preset'},
                                # layout={'name': 'circle'},
                                # layout={'name': 'cose'},

                                style={'width': '100%', 'height': '75vh'},
                                # stylesheet=CY_STYLE_STATIC, # TODO
                                # elements=cygraph,
                                className='factory-graph'
                            )
                        ]
                    )
                ),
                dbc.CardFooter(
                    id='graph-positioning-container',
                    style={'display': 'None'},
                    children=[
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    dbc.Button('Save node position', id='graph-positioning-save-button', n_clicks=0),
                                    style={'height': '100%'}
                                ),
                                dbc.Col(
                                    children=[
                                        dbc.Alert(
                                            id='graph-positioning-saved-notifier',
                                            class_name='inline-alert',
                                            is_open=False,
                                            duration=5000
                                        )
                                    ],
                                    style={'height': '100%'}
                                ),


                            ],
                            style={'height': '40px'})
                    ]
                )
            ]),
        ]
    )


def __get_cytoscape_base_node(node: BaseNode,
                              node_type: str = SelectedElementTypes.UNSPECIFIED_NODE_TYPE.value):
    # Restore node positioning where available:
    pox_x = node.visualization_positioning_x if node.visualization_positioning_x is not None else 0
    pox_y = node.visualization_positioning_y if node.visualization_positioning_y is not None else 0

    return {
        'data': {
            'id': node.id_short,
            'label': node.id_short,
            'type': node_type,
            'iri': node.iri,
            'description': node.description
        },
        'classes': [node_type],
        'position': {'x': pox_x, 'y': pox_y},
    }


def __get_cytoscape_machine(machine: MachineDeep):
    element_dict = __get_cytoscape_base_node(machine, SelectedElementTypes.MACHINE.value)

    return element_dict


def __get_cytoscape_timeseries(timeseries: TimeseriesDeep):
    element_dict = __get_cytoscape_base_node(timeseries, SelectedElementTypes.TIMESERIES_INPUT.value)

    return element_dict


def __get_cytoscape_base_edge(node_from: BaseNode,
                              node_to: BaseNode,
                              edge_type: str = SelectedElementTypes.UNSPECIFIED_EDGE_TYPE.value):
    return {
        'data': {
            'source': node_from.id_short,
            'target': node_to.id_short,
        },
        'classes': [edge_type],
    }


def __get_cytoscape_timeseries_machine_edge(timeseries: TimeseriesDeep, machine: MachineDeep):
    element_dict = __get_cytoscape_base_edge(machine, timeseries, SelectedElementTypes.HAS_TIMESERIES.value)

    return element_dict


def get_cytoscape_elements(machines_deep: List[MachineDeep]):
    cytoscape_elements = []

    for machine in machines_deep:
        # Machines:
        cytoscape_elements.append(__get_cytoscape_machine(machine))

        for timeseries in machine.timeseries:
            # Timeseries:
            cytoscape_elements.append(__get_cytoscape_timeseries(timeseries))
            # Timeseries relationships:
            cytoscape_elements.append(__get_cytoscape_timeseries_machine_edge(timeseries, machine))

    return cytoscape_elements
