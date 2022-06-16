import dash_bootstrap_components as dbc
from dash import html

from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement


def get_layout():
    """
    Layout of the graph selector.
    Contains both the intermediate selector storage storing information about the selected node OR edge,
    as well as the graphical output.
    :return:
    """
    return html.Div(
        children=[
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


def get_info_content(selected_el_json):
    """
        Builds the info table for identifying the selected node (if any selected)
        :param selected_el_json: the selected element (json)
        :return:
        """

    header_row = html.Tr(
        children=[
            html.Td(children=['Selected element:']),
        ],
        className='custom-table-header'
    )

    info_rows = []

    if selected_el_json is None:
        info_rows.append(
            html.Tr(
                children=[
                    html.Td(children=['Nothing selected']),
                ],
                className='custom-table-row'
            )
        )
    else:
        selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

        info_rows.append(
            html.Tr(
                children=[
                    html.Td(children=['IdShort:'], ),
                    html.Td(selected_el.id_short)
                ],
                className='custom-table-row'
            )
        )

        info_rows.append(
            html.Tr(
                children=[
                    html.Td(children=['Node / Edge:'], ),
                    html.Td(
                        'NODE' if selected_el.is_node else 'EDGE'
                    )
                ],
                className='custom-table-row'
            )
        )

        info_rows.append(
            html.Tr(
                children=[
                    html.Td(children=['Type:'], ),
                    html.Td(selected_el.type.value)
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
