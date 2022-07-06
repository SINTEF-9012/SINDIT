from frontend.app import app
from dash.dependencies import Input, Output
from datetime import timedelta
from frontend.left_sidebar.datetime_selector.datetime_selector_layout import (
    transform_value,
)

from frontend.left_sidebar.global_information import global_information_layout

print("Initializing datetime selector callbacks...")


@app.callback(
    Output("datetime-selector-date", "disabled"),
    Output("datetime-selector-time", "disabled"),
    Input("realtime-switch-input", "value"),
)
def update_output(realtime_toggle):
    """
    Toggles whether the time selectors are active. Active when realtime-mode is disabled
    :param realtime_toggle:
    :return:
    """
    if realtime_toggle:
        return True, True
    else:
        return False, False
