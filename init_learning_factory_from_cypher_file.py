"""
SINDIT: fischertechnik learning factory

author: Timo Peter <timo.peter@sintef.no>

"""
import configparser
import sys
import py2neo
import environment.environment as env
from config import global_config as cfg

LEARNING_FACTORY_CYPHER_FILE = "learning_factory.cypher"

# Read Config
config = configparser.ConfigParser()
config.read(cfg.PATH_TO_CONFIG)
NEO4J_URI = env.NEO4J_FACTORY
NEO4J_USER = config["factory-neo4j"]["user"]
NEO4J_PASS = config["factory-neo4j"]["pass"]

if __name__ == "__main__":

    user_input = input(
        "Do you really want to initialize the toy factory Knowledge Graph Digital Twin instance? Current data will be lost! (y/n)"
    )
    if user_input != "y":
        sys.exit()

    user_input = input("Are you sure? (y/n)")
    if user_input != "y":
        sys.exit()

    g = py2neo.Graph(NEO4J_URI)

    tx = g.begin()

    # Delete everything
    g.delete_all()

    with open(LEARNING_FACTORY_CYPHER_FILE, "r") as cypher_file:
        cypher_query = cypher_file.read().strip()
    g.run(cypher_query)

    graph_property_node = py2neo.Node("GRAPH_PROP_NODE", name="learning_factory")

    m = py2neo.Node(
        "MACHINE",
        name="HBW",
        description="High Bay Warehouse",
        group="NONE",
        num_parts_in=0,
        num_parts_out=0,
        amount_in=0,
        amount_out=0,
        processing_time=0,
        position_on_dash=[-73, 70],
        size_on_dash=[30, 20],
        shape_on_dash="round-rectangle",
        color_on_dash="#b19cd9",
    )

    g.commit(tx)
