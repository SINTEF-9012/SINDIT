import requests
import json
import pandas as pd

import environment.environment as stngs

API_URI = stngs.FAST_API_URI

def get_json(relative_path: str):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return:
    """
    return requests.get(API_URI + relative_path).json()

def get_as_dict(relative_path: str):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return:
    """
    return json.loads(get_json(relative_path))

def get_dataframe(relative_path: str):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return:
    """
    return pd.DataFrame.from_dict(get_as_dict(relative_path))
