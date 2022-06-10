import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

from frontend import api_client
from frontend.right_sidebar.graph_selector import graph_selector_util


def get_layout():
    """
    Layout of the graph selector.
    Contains both the intermediate selector storage storing information about the selected node OR edge,
    as well as the graphical output.
    :return:
    """
    return html.Div(
        children=[
            # Storage for accessing the selected element
            dcc.Store(id='selected-graph-element-store'),
            # Graphical output:
            html.Pre(
                id='selected-graph-element-info',
                className='custom-table',
                children=[
                    get_info_content(None)
                ]
            ),
        ]
    )


def get_info_content(selected_el):
    """
        Builds the info table for identifying the selected node (if any selected)
        :param selected_el: the selected element (json)
        :return:
        """

    header_row = html.Tr(
        children=[
            html.Td(children=['Selected element:']),
        ],
        className='custom-table-header'
    )

    info_rows = []

    if selected_el is None:
        info_rows.append(
            html.Tr(
                children=[
                    html.Td(children=['Nothing selected']),
                ],
                className='custom-table-row'
            )
        )
    else:
        info_rows.append(
            html.Tr(
                children=[
                    html.Td(children=['IdShort:'], ),
                    html.Td(graph_selector_util.get_id_short(selected_el))
                ],
                className='custom-table-row'
            )
        )

        info_rows.append(
            html.Tr(
                children=[
                    html.Td(children=['Node / Edge:'], ),
                    html.Td(graph_selector_util.get_node_edge(selected_el).value)
                ],
                className='custom-table-row'
            )
        )

        info_rows.append(
            html.Tr(
                children=[
                    html.Td(children=['Type:'], ),
                    html.Td(graph_selector_util.get_type(selected_el).value)
                ],
                className='custom-table-row'
            )
        )

    return dbc.Table(
        children=[
            html.Tbody(
                children=[header_row] + info_rows
            )
        ],
        bordered=False
    )
