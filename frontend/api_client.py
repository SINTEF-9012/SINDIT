import requests
import json

import environment.environment as stngs

API_URI = stngs.FAST_API_URI

def get(relative_path: str):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return:
    """
    return requests.get(API_URI + relative_path).json()
