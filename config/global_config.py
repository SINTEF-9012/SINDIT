import configparser
from enum import Enum

PATH_TO_CONFIG = 'config/sindit.cfg'

"""
Allows an easy access to the global configuration parameters
"""

config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG)


class ConfigGroups(Enum):
    FRONTEND = "frontend"
    API = "api"
    GRAPH = "neo4j-knowledge-graph"


def get_str(group: ConfigGroups, key: str):
    return config[group.value][key]


def get_int(group: ConfigGroups, key: str):
    return int(config[group.value][key])

def get_float(group: ConfigGroups, key: str):
    return float(config[group.value][key])
