from datetime import datetime
from dash.dependencies import Input, Output, State
import pandas as pd
from dateutil import tz

from frontend import api_client
from frontend.app import app
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.node_data_tab.live_sensor_readings import (
    timeseries_graph_layout,
)
from graph_domain.factory_graph_types import NodeTypes
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
    get_configuration_float,
)

sensor_ID = None

LIVE_SENSOR_DISPLAY_DURATION = get_configuration_float(
    group=ConfigGroups.FRONTEND, key="current_timeseries_duration"
)


print("Initializing sensor callbacks...")


@app.callback(
    Output("live-update-timeseries", "figure"),
    Input("interval-component", "n_intervals"),
    State("selected-graph-element-store", "data"),
    Input("realtime-switch-input", "value"),
    Input("datetime-selector-date", "value"),
    Input("datetime-selector-time", "value"),
)
def update_timeseries_graph(
    n, selected_el_json, realtime_toggle, selected_date_str, selected_time_str
):

    fig = timeseries_graph_layout.get_figure()

    # Cancel if nothing selected
    if selected_el_json is None:
        return fig

    data = pd.DataFrame(columns=["time", "value"])

    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    # Cancel if anything else than timeseries is selected
    if selected_el.type != NodeTypes.TIMESERIES_INPUT.value:
        print("Trying to visualize timeseries from non-timeseries element...")
        return fig

    # API call for the dataframe
    if realtime_toggle:
        data = api_client.get_dataframe(
            relative_path="/timeseries/current_range",
            iri=selected_el.iri,
            duration=LIVE_SENSOR_DISPLAY_DURATION,
        )
    else:
        selected_time = datetime.fromisoformat(selected_time_str).time()
        selected_date = datetime.fromisoformat(selected_date_str).date()
        selector_tz = tz.gettz(
            get_configuration(group=ConfigGroups.FRONTEND, key="timezone")
        )
        date_time = datetime.combine(
            date=selected_date,
            time=selected_time,
            tzinfo=selector_tz,
        )

        # selected_date_time = datetime.
        # selected_time_str
        # selected_time_str.
        # datetime.now().time

        data = api_client.get_dataframe(
            relative_path="/timeseries/range",
            iri=selected_el.iri,
            duration=LIVE_SENSOR_DISPLAY_DURATION,
            date_time_str=date_time.isoformat(),
        )

    fig.add_trace(
        trace={
            "x": data["time"],
            "y": data["value"],
            "mode": "lines+markers",
            "type": "scatter",
        },
        row=1,
        col=1,
    )

    # Layouting...
    fig.update_traces(marker_size=8, marker_line=None, mode="markers")

    return fig
