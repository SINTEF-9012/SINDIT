from dash import html


def get_layout():
    return html.Div(id='global-information-container')


def get_content():
    return html.Div("Will contain connection status etc...")
    # TODO: connection status, time, node count, edge count...
    # Directly load from the API as this will be reloaded frequently
