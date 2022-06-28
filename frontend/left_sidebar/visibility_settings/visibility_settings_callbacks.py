from frontend.app import app
from dash.dependencies import Input, Output

from frontend import resources_manager
from frontend.main_column.factory_graph.factory_graph_layout import (
    CY_GRAPH_STYLE_STATIC,
)
from graph_domain.factory_graph_types import (
    NODE_TYPE_STRINGS,
    RELATIONSHIP_TYPES_FOR_NODE_TYPE,
    NodeTypes,
)

print("Initializing visibility settings callbacks...")


@app.callback(
    Output("cytoscape-graph", "stylesheet"), Input("visibility-switches-input", "value")
)
def update_output(active_switches):
    """
    Toggles the visibility of element types in the main graph
    :param value:
    :return:
    """
    deactivated_switches = [
        switch for switch in NODE_TYPE_STRINGS if switch not in active_switches
    ]

    invisibility_styles = []

    for inactive_switch in deactivated_switches:
        # Hide nodes from that type:
        invisibility_styles.append(
            {"selector": f".{inactive_switch}", "style": {"opacity": 0}}
        )
        # Hide connected relationships:
        for relationship_type in RELATIONSHIP_TYPES_FOR_NODE_TYPE.get(inactive_switch):
            invisibility_styles.append(
                {"selector": f".{relationship_type}", "style": {"opacity": 0}}
            )

    return CY_GRAPH_STYLE_STATIC + invisibility_styles
