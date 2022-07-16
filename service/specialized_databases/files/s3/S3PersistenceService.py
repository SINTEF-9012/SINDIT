from datetime import datetime
import io
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point
import pandas as pd
from urllib3.exceptions import ReadTimeoutError
import boto3
from botocore.client import Config

from graph_domain.DatabaseConnectionNode import DatabaseConnectionNode
from service.exceptions.IdNotFoundException import IdNotFoundException
from service.specialized_databases.files.FilesPersistenceService import (
    FilesPersistenceService,
)


class S3PersistenceService(FilesPersistenceService):
    """ """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.client = boto3.client(
            "s3",
            endpoint_url=self.host + ":" + self.port,
            aws_access_key_id=self.user,
            aws_secret_access_key=self.key,
            config=Config(signature_version="s3v4"),
            # region_name="eu-north-1",  # ignore region functionality
        )

        self.resource = boto3.resource(
            "s3",
            endpoint_url=self.host + ":" + self.port,
            aws_access_key_id=self.user,
            aws_secret_access_key=self.key,
            config=Config(signature_version="s3v4"),
            # region_name="eu-north-1",  # ignore region functionality
        )

        self.bucket_name = self.group

        self.bucket = self.resource.Bucket(self.bucket_name)

    # override
    def read_file(
        self,
        iri: str,
    ):
        """
        Reads
        :param iri:
        :return:
        :raise IdNotFoundException: if the iri is not found
        """
        object = self.bucket.Object(iri)
        response = object.get()
        file_stream = response["Body"]
        return file_stream
