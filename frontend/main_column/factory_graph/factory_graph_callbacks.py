from datetime import datetime

import pytz
from dash.dependencies import Input, Output, State

from frontend import api_client
from frontend.app import app
from frontend.main_column.factory_graph import factory_graph_layout
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from graph_domain.AssetNode import AssetNodeDeep


print("Initializing factory graph callbacks...")


@app.callback(
    Output("cytoscape-graph", "elements"), Input("graph-reload-button", "n_clicks")
)
def update_factory_graph(n):
    """
    Updates the main graph: Loads the nodes and edges from Neo4J
    :param n:
    :return:
    """
    machines_deep_json = api_client.get("/graph/machines_deep")
    machines_deep = [AssetNodeDeep.from_json(m) for m in machines_deep_json]
    cygraph_elements = factory_graph_layout.get_cytoscape_elements(
        assets_deep=machines_deep
    )

    return cygraph_elements


@app.callback(
    [
        Output("selected-graph-element-store", "data"),
        Output("selected-graph-element-timestamp", "data"),
    ],
    [
        Input("kg-container", "n_clicks"),
        State("selected-graph-element-timestamp", "data"),
        State("cytoscape-graph", "tapNode"),
        State("cytoscape-graph", "tapEdge"),
    ],
    prevent_initial_call=True,
)
def store_selected_element_info(n_clicks, last_click_time_str, tap_node, tap_edge):
    """
    Called whenever an element in the graph is selected (or de-selected).
    Stores the selected element to be available for other callbacks
    :param n_clicks:
    :param last_click_time_str:
    :param tap_edge:
    :param tap_node:
    :return:
    """
    if last_click_time_str is not None:
        last_click_time = datetime.fromisoformat(last_click_time_str)
    else:
        # Min available timestamp, so that the current one will be considered newer
        last_click_time = datetime.fromtimestamp(0, tz=pytz.UTC)

    if (
        tap_node is not None
        and datetime.fromtimestamp(tap_node["timeStamp"] / 1000.0, tz=pytz.UTC)
        > last_click_time
    ):
        # Currently selected a node:
        selected_el = GraphSelectedElement.from_tap_node(tap_node)
        new_selected_el_json = selected_el.to_json()
        new_click_time = datetime.fromtimestamp(
            tap_node["timeStamp"] / 1000.0, tz=pytz.UTC
        )
    elif (
        tap_edge is not None
        and datetime.fromtimestamp(tap_edge["timeStamp"] / 1000.0, tz=pytz.UTC)
        > last_click_time
    ):
        # Currently selected an edge:
        selected_el = GraphSelectedElement.from_tap_edge(tap_edge)
        new_selected_el_json = selected_el.to_json()
        new_click_time = datetime.fromtimestamp(
            tap_edge["timeStamp"] / 1000.0, tz=pytz.UTC
        )
    else:
        # Deselected the element (click into the white space)
        new_selected_el_json = None
        new_click_time = last_click_time

    return new_selected_el_json, new_click_time.isoformat()


@app.callback(
    Output("graph-positioning-saved-notifier", "children"),
    Output("graph-positioning-saved-notifier", "is_open"),
    Input("graph-positioning-save-button", "n_clicks"),
    State("selected-graph-element-store", "data"),
    prevent_initial_call=True,
)
def update_node_position(n_clicks, selected_el_json):
    """
    Called when the user selects to store the altered position of a node
    :param n_clicks:
    :param selected_el_json:
    :return:
    """
    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    api_client.patch(
        "/graph/node_position",
        iri=selected_el.iri,
        pos_x=selected_el.position_x,
        pos_y=selected_el.position_y,
    )

    # Notify the user with an auto-dismissing alert:
    return f"Node position saved successfully:\n{datetime.now().isoformat()}", True


@app.callback(
    Output("graph-positioning-container", "style"),
    Input("selected-graph-element-store", "data"),
    Input("cytoscape-graph", "elements"),
    prevent_initial_call=True,
)
def toggle_layout_saver_visibility(selected_el_json, elements):
    """
    Called whenever a element is selected (or de-selected) in the graph, or when the graph changes.
    Provides the user with a visible save-functionality for the altered node position, if a node is selected, that
    the user moved via drag and drop.
    :param selected_el_json:
    :param elements:
    :return:
    """
    if selected_el_json is not None:
        selected_el: GraphSelectedElement = GraphSelectedElement.from_json(
            selected_el_json
        )
        if selected_el.is_node:
            # Get the last persisted position for comparison
            stored_el_pos = next(
                (
                    element["data"].get("persisted_pos")
                    for element in elements
                    if element["data"].get("iri") == selected_el.iri
                ),
                # Default:
                {"x": 0, "y": 0},
            )
            if selected_el.position_x != stored_el_pos.get(
                "x"
            ) or selected_el.position_y != stored_el_pos.get("y"):
                # Show save position button:
                return {}

    # Do not show in any other case
    return {"display": "None"}
