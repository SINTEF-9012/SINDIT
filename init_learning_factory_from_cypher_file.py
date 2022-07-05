"""
SINDIT: fischertechnik learning factory

author: Timo Peter <timo.peter@sintef.no>

"""
import sys
import py2neo
from util.environment_and_configuration import get_environment_variable

LEARNING_FACTORY_CYPHER_FILE = "learning_factory_instance/learning_factory.cypher"

# Read Config
NEO4J_HOST = get_environment_variable(key="NEO4J_DB_HOST", optional=False)
NEO4J_PORT = get_environment_variable(key="NEO4J_DB_PORT", optional=False)
NEO4J_URI = NEO4J_HOST + ":" + NEO4J_PORT
NEO4J_USER = get_environment_variable(
    key="NEO4J_DB_USER", optional=True, default="neo4j"
)
NEO4J_PASS = get_environment_variable(key="NEO4J_DB_PW", optional=True, default="neo4j")

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
