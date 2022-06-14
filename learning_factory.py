"""
SINDIT: fischertechnik learning factory

author: Timo Peter <timo.peter@sintef.no>

"""
import dtwin.dtmachine as dtMachine
import dtwin.dtqueue as dtQueue
import dtwin.dtsensor as dtSensor
import dtwin.dttypes as dtTypes
import dtwin.dtpart as dtPart
import json
import networkx as nx
import datetime
import dateutil.parser
from dtwin.dtfactory import dtFactory
import simpy
import configparser
import py2neo
import environment.environment as env
from enum import Enum, unique
from config import global_config as cfg

# Read Config
config = configparser.ConfigParser()
config.read(cfg.PATH_TO_CONFIG)
NEO4J_URI = env.NEO4J_FACTORY_OLD
NEO4J_USER = config['factory-neo4j']['user']
NEO4J_PASS = config['factory-neo4j']['pass']

if __name__ == '__main__':

    g = py2neo.Graph(NEO4J_URI)

    # first we delete everything
    g.delete_all()

    tx = g.begin()

    graph_property_node = py2neo.Node('GRAPH_PROP_NODE',
                                      name="learning_factory")

    m = py2neo.Node("MACHINE",
                    name="HBW",
                    description="High Bay Warehouse",
                    group="NONE",
                    num_parts_in=0,
                    num_parts_out=0,
                    amount_in=0,
                    amount_out=0,
                    processing_time=0,
                    position_on_dash=[-73,70],
                    size_on_dash=[30,20],
                    shape_on_dash="round-rectangle",
                    color_on_dash="#b19cd9")
    tx.create(m)

    tx.commit()

