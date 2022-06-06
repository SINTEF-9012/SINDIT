from dash import html
import dash_bootstrap_components as dbc
from app import app

def get_layout():
    """
    Layout of the navbar
    :return:
    """
    return dbc.Navbar(
        children=[
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=app.get_asset_url('sintef_blue.png'), height="32px")),
                    ],
                    align="center"
                ),
                href="https://www.sintef.no"
            ),
        ]
    )