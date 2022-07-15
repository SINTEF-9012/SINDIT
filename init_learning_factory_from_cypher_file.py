"""
SINDIT: fischertechnik learning factory

author: Timo Peter <timo.peter@sintef.no>

"""
import sys
import py2neo
from util.environment_and_configuration import get_environment_variable
import boto3
from botocore.client import Config

LEARNING_FACTORY_CYPHER_FILE = "learning_factory_instance/learning_factory.cypher"
LEARNING_FACTORY_BINARIES_IMPORT_FOLDER = "./learning_factory_instance/binaries_import/"

# Read Config
NEO4J_HOST = get_environment_variable(key="NEO4J_DB_HOST", optional=False)
NEO4J_PORT = get_environment_variable(key="NEO4J_DB_PORT", optional=False)
NEO4J_URI = NEO4J_HOST + ":" + NEO4J_PORT
NEO4J_USER = get_environment_variable(
    key="NEO4J_DB_USER", optional=True, default="neo4j"
)
NEO4J_PASS = get_environment_variable(key="NEO4J_DB_PW", optional=True, default="neo4j")

S3_HOST = get_environment_variable(key="MINIO_S3_HOST", optional=False)
S3_PORT = get_environment_variable(key="MINIO_S3_PORT", optional=False)
S3_URI = S3_HOST + ":" + S3_PORT
S3_USER = get_environment_variable(
    key="MINIO_S3_USER", optional=True, default="sindit_minio_access_key"
)
S3_PASSWORD = get_environment_variable(
    key="MINIO_S3_PASSWORD", optional=True, default="sindit_minio_secret_key"
)
S3_BUCKET_NAME = "sindit"  # Bucket name stored in graph!


def setup_knowledge_graph():
    g = py2neo.Graph(NEO4J_URI)

    tx = g.begin()

    # Delete everything
    g.delete_all()

    with open(LEARNING_FACTORY_CYPHER_FILE, "r") as cypher_file:
        cypher_query = cypher_file.read().strip()
    g.run(cypher_query)

    graph_property_node = py2neo.Node("GRAPH_PROP_NODE", name="learning_factory")

    g.commit(tx)


def import_binary_data():

    s3_client = boto3.client(
        "s3",
        endpoint_url=S3_URI,
        aws_access_key_id=S3_USER,
        aws_secret_access_key=S3_PASSWORD,
        config=Config(signature_version="s3v4"),
        # region_name="eu-north-1",  # ignore region functionality
    )

    s3_resource = boto3.resource(
        "s3",
        endpoint_url=S3_URI,
        aws_access_key_id=S3_USER,
        aws_secret_access_key=S3_PASSWORD,
        config=Config(signature_version="s3v4"),
        # region_name="eu-north-1",  # ignore region functionality
    )

    if not S3_BUCKET_NAME in [b["Name"] for b in s3_client.list_buckets()["Buckets"]]:
        s3_client.create_bucket(Bucket=S3_BUCKET_NAME)

    bucket = s3_resource.Bucket(S3_BUCKET_NAME)

    bucket.objects.all().delete()

    g = py2neo.Graph(NEO4J_URI)

    file_list = g.run("MATCH (f:SUPPLEMENTARY_FILE) RETURN f.file_name, f.iri").data()

    print("Storing files in S3:")
    for file in file_list:
        print(f"{file['f.file_name']}")

        bucket.upload_file(
            LEARNING_FACTORY_BINARIES_IMPORT_FOLDER + file["f.file_name"], file["f.iri"]
        )

    # upload a file from local file system '/home/john/piano.mp3' to bucket 'songs' with 'piano.mp3' as the object name.
    # s3.Bucket("songs").upload_file(
    #     LEARNING_FACTORY_BINARIES_IMPORT_FOLDER + "", "piano.mp3"
    # )

    # # download the object 'piano.mp3' from the bucket 'songs' and save it to local FS as /tmp/classical.mp3
    # s3.Bucket("songs").download_file("piano.mp3", "/tmp/classical.mp3")


if __name__ == "__main__":

    user_input = input(
        "Do you really want to initialize the toy factory Knowledge Graph Digital Twin instance? Current data will be lost! (y/n)"
    )
    if user_input != "y":
        sys.exit()

    user_input = input("Are you sure? (y/n)")
    if user_input != "y":
        sys.exit()

    setup_knowledge_graph()
    import_binary_data()
