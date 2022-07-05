from datetime import datetime
import requests
import json
import pandas as pd

from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
    get_environment_variable,
)

API_URI = (
    get_environment_variable("FAST_API_HOST")
    + ":"
    + get_environment_variable("FAST_API_PORT")
)


def get(relative_path: str, **kwargs):
    """
    Get request to the specified api endpoint
    :param relative_path:
    :return: the response json as dict
    """
    resp_dict = requests.get(API_URI + relative_path, params=kwargs).json()

    if isinstance(resp_dict, str):
        # Sometimes, the json is still represented as string instead of dict
        resp_dict = json.loads(resp_dict)

    return resp_dict


def get_dataframe(relative_path: str, **kwargs):
    """
    Get request to the specified api endpoint. Deserializes to dataframe
    :param relative_path:
    :return:
    """
    df_dict = get(relative_path, **kwargs)

    df = pd.DataFrame.from_dict(df_dict)

    # Convert string timestamp to actual tz data type
    df["time"] = df["time"].map(
        lambda t_string: datetime.strptime(t_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    )
    # Set UTC timezone (trans)
    df["time"] = df["time"].map(lambda t: t.tz_localize("UTC"))

    df["time"] = df["time"].map(
        lambda t: t.tz_convert(
            get_configuration(group=ConfigGroups.FRONTEND, key="timezone")
        )
    )

    return df


def patch(relative_path: str, **kwargs):
    requests.patch(API_URI + relative_path, params=kwargs)
