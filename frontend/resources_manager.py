import requests
import json

from frontend.app import app


def load_json(path):
    """
    Receives or reads a JSON resource locally or via network
    :param path: local path
    :return: the json object
    """
    asset_url = app.get_asset_url(path)

    if 'http' in asset_url:
        return requests.get(asset_url).json()
    else:
        if asset_url[0] == '/':
            asset_url = asset_url[1:]

        with open(asset_url, 'rb') as f:
            obj = json.load(f)
        return obj
