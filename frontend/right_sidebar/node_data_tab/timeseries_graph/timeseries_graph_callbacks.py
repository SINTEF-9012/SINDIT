from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State
import pandas as pd
from dateutil import tz
from dash.exceptions import PreventUpdate

from frontend import api_client
from frontend.app import app
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.node_data_tab.timeseries_graph import (
    timeseries_graph_layout,
)
from graph_domain.factory_graph_types import NodeTypes
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
    get_configuration_float,
)

sensor_ID = None

TIMESERIES_MAX_DISPLAYED_ENTRIES = get_configuration_float(
    group=ConfigGroups.FRONTEND, key="timeseries_max_displayed_entries"
)


print("Initializing timeseries callbacks...")


@app.callback(
    Output("timeseries-graph-update-interval-passthrough", "children"),
    Input("interval-component", "n_intervals"),
    Input("realtime-switch-input", "value"),
    State("timeseries-graph-update-interval-passthrough", "children"),
)
def timeseries_graph_interval(n, realtime_toggle, pseudo_element_input):
    """Updates a pseudo component whenever the realtime-graph shall be updated.
    Used to avoid unnscessary updates while viewing historic data.

    Args:
        n (_type_): _description_
        realtime_toggle (_type_): _description_

    Returns:
        _type_: _description_
    """
    if not isinstance(pseudo_element_input, int):
        return 0

    if realtime_toggle:
        return pseudo_element_input + 1
    else:
        raise PreventUpdate()


@app.callback(
    Output("timeseries-graph", "figure"),
    Output("timeseries-graph-result-count-info", "children"),
    Output("timeseries-graph-aggregate-info", "children"),
    Input("timeseries-graph-update-interval-passthrough", "children"),
    State("selected-graph-element-store", "data"),
    Input("realtime-switch-input", "value"),
    Input("datetime-selector-date", "value"),
    Input("datetime-selector-time", "value"),
    Input("datetime-selector-range-days", "value"),
    Input("datetime-selector-range-hours", "value"),
    Input("datetime-selector-range-min", "value"),
    Input("datetime-selector-range-sec", "value"),
)
def update_timeseries_graph(
    n,
    selected_el_json,
    realtime_toggle,
    selected_date_str,
    selected_time_str,
    duration_days,
    duration_hours,
    duration_mins,
    duration_secs,
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

    duration: timedelta = timedelta(
        days=duration_days,
        hours=duration_hours,
        minutes=duration_mins,
        seconds=duration_secs,
    )

    # API call for the dataframe
    if realtime_toggle:
        date_time = datetime.now()
    else:
        if isinstance(selected_time_str, str) and selected_time_str != "":
            selected_time = datetime.fromisoformat(selected_time_str).time()
        else:
            selected_time = datetime.now().time()

        if isinstance(selected_date_str, str) and selected_date_str != "":
            selected_date = datetime.fromisoformat(selected_date_str).date()
        else:
            selected_date = datetime.now().date()

        selector_tz = tz.gettz(
            get_configuration(group=ConfigGroups.FRONTEND, key="timezone")
        )
        date_time = datetime.combine(
            date=selected_date,
            time=selected_time,
            tzinfo=selector_tz,
        )

    # API call for the count of readings
    readings_count = int(
        api_client.get(
            relative_path="/timeseries/entries_count",
            iri=selected_el.iri,
            duration=duration.total_seconds(),
            date_time_str=date_time.isoformat(),
        )
    )

    # Filtering to avoid loading to large readings datasets
    if readings_count > TIMESERIES_MAX_DISPLAYED_ENTRIES:
        if duration.total_seconds() > timedelta(days=2).total_seconds():
            # More than two days -> use hourly aggregation
            aggregation_window_s = timedelta(hours=1).total_seconds()
        elif duration.total_seconds() > timedelta(hours=6).total_seconds():
            aggregation_window_s = timedelta(minutes=10).total_seconds()
        elif duration.total_seconds() > timedelta(hours=2).total_seconds():
            aggregation_window_s = timedelta(minutes=1).total_seconds()
        elif duration.total_seconds() > timedelta(minutes=10).total_seconds():
            aggregation_window_s = timedelta(seconds=1).total_seconds()
        else:
            aggregation_window_s = timedelta(milliseconds=100).total_seconds()

        aggregation_window_ms = int(aggregation_window_s * 1000)
    else:
        aggregation_window_ms = None

    # API call for the readings
    data = api_client.get_dataframe(
        relative_path="/timeseries/range",
        iri=selected_el.iri,
        duration=duration.total_seconds(),
        date_time_str=date_time.isoformat(),
        aggregation_window_ms=aggregation_window_ms,
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

    # Aggregate info
    result_count_str = f"Total count of entries for given time-frame: {readings_count}."
    aggregate_info_str = (
        f"Only displaying the first reading each per {timedelta(milliseconds=aggregation_window_ms)} (d:min:sec)."
        if aggregation_window_ms is not None
        else ""
    )

    return fig, result_count_str, aggregate_info_str
