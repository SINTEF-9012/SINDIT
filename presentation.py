from frontend.app import app
from frontend import page_layout

# Import callback files (indirectly used through annotation)

# noinspection PyUnresolvedReferences
from frontend.left_sidebar.visibility_settings import visibility_settings_callbacks

# noinspection PyUnresolvedReferences
from frontend.left_sidebar.global_information import global_information_callbacks

# noinspection PyUnresolvedReferences
from frontend.left_sidebar.datetime_selector import datetime_selector_callbacks

# noinspection PyUnresolvedReferences
from frontend.main_column.factory_graph import factory_graph_callbacks

# noinspection PyUnresolvedReferences
from frontend.right_sidebar import right_sidebar_callbacks

# noinspection PyUnresolvedReferences
from frontend.right_sidebar.graph_selector_info import graph_selector_info_callbacks

# noinspection PyUnresolvedReferences
from frontend.right_sidebar.node_data_tab.timeseries_graph import (
    timeseries_graph_callbacks,
)


"""
Main entry point for the presentation layer
Separated from app.py to avoid circular dependencies with callback files importing the "app" instance. 
"""

# #############################################################################
# Launch frontend
# #############################################################################
if __name__ == "__main__":
    # Initialize layout
    app.layout = page_layout.get_layout()

    app.run_server(host="0.0.0.0", debug=False, port=8050, use_reloader=False)
