import requests
import json
import pandas as pd

import environment.environment as env

API_URI = env.FAST_API_URI

def get(relative_path: str):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response json as dict
    """
    resp_dict = requests.get(API_URI + relative_path).json()

    if isinstance(resp_dict, str):
        # Sometimes, the json is still represented as string instead of dict
        resp_dict = json.loads(resp_dict)

    return resp_dict

def get_dataframe(relative_path: str):
    """
    Get request to the specified api endpoint. Deserializes to dataframe
    :param relative_path:
    :return:
    """
    return pd.DataFrame.from_dict(get(relative_path))
