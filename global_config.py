import configparser

PATH_TO_CONFIG = 'sindit.cfg'

"""
Allows an easy access to the global configuration parameters
"""

config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG)
