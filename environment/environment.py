import os
from os.path import join, dirname
from dotenv import load_dotenv

# if not set let's assume our one and only env file
if os.getenv("ENVIRONMENT_FILE") is None:
    # os.environ["ENVIRONMENT_FILE"] = "local_deployment.env"
    os.environ["ENVIRONMENT_FILE"] = "docker_deployment.env"

dotenv_path = join(dirname(__file__), os.getenv("ENVIRONMENT_FILE"))
load_dotenv(dotenv_path=dotenv_path, override=True)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FAST_API_URI = os.getenv("FAST_API_URI")
DASHBOARD_URI = os.getenv("DASHBOARD_URI")
NEO4J_FACTORY = os.getenv("NEO4J_FACTORY")

# Deprecated:
# TODO: remove
KAFKA_PRODUCER_URI = os.getenv("KAFKA_PRODUCER_URI")
INFLUXDB_URI = os.getenv("INFLUXDB_URI")
INFLUXDB_PORT = os.getenv("INFLUXDB_PORT")
NEO4J_PARTS = os.getenv("NEO4J_PARTS")
NEO4J_FACTORY_OLD = os.getenv("NEO4J_FACTORY_OLD")