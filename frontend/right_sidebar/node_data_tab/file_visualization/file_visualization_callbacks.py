from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State
import pandas as pd
from dateutil import tz
from dash.exceptions import PreventUpdate
from dash import dcc
from frontend import api_client
from frontend.app import app
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.node_data_tab.timeseries_graph import (
    timeseries_graph_layout,
)
from graph_domain.SupplementaryFileNode import SupplementaryFileNodeFlat
from graph_domain.factory_graph_types import NodeTypes
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
    get_configuration_float,
)

print("Initializing file visualization callbacks...")


@app.callback(
    Output("suppl_file_download-notifier", "children"),
    Output("suppl_file_download-notifier", "is_open"),
    Input("suppl_file_download_button", "n_clicks"),
    prevent_initial_call=True,
)
def download_file_notifier(n_clicks):

    return (
        f"Download triggered. This can take a while...",
        True,
    )


@app.callback(
    Output("suppl_file_download", "data"),
    Input("suppl_file_download_button", "n_clicks"),
    State("selected-graph-element-store", "data"),
    prevent_initial_call=True,
)
def download_file(n_clicks, selected_el_json):

    # Cancel if nothing selected
    if selected_el_json is None:
        raise PreventUpdate()

    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    # Cancel if anything else than a file is selected
    if selected_el.type != NodeTypes.SUPPLEMENTARY_FILE.value:
        print("Trying to download file for non-file element...")
        raise PreventUpdate()

    suppl_file_data = api_client.get_raw(
        relative_path="/supplementary_file/data",
        iri=selected_el.iri,
    )

    suppl_file_details_dict = api_client.get(
        relative_path="/supplementary_file/details",
        iri=selected_el.iri,
    )
    suppl_file_details: SupplementaryFileNodeFlat = SupplementaryFileNodeFlat.from_dict(
        suppl_file_details_dict
    )

    return dcc.send_bytes(src=suppl_file_data, filename=suppl_file_details.file_name)


# @app.callback(
#     Output("graph-positioning-saved-notifier", "children"),
#     Output("graph-positioning-saved-notifier", "is_open"),
#     Input("graph-positioning-save-button", "n_clicks"),
#     State("selected-graph-element-store", "data"),
#     prevent_initial_call=True,
# )
# def update_node_position(n_clicks, selected_el_json):
#     """
#     Called when the user selects to store the altered position of a node
#     :param n_clicks:
#     :param selected_el_json:
#     :return:
#     """
#     selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

#     api_client.patch(
#         "/node_position",
#         iri=selected_el.iri,
#         pos_x=selected_el.position_x,
#         pos_y=selected_el.position_y,
#     )

#     # Notify the user with an auto-dismissing alert:
#     return f"Node position saved successfully:\n{datetime.now().isoformat()}", True
