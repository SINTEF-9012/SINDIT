import time
from datetime import datetime

from influxdb_client.client.write_api import  SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point
import global_config as cfg

class TimeseriesPersistenceService(object):
    """

    """
    __instance = None

    @staticmethod
    def instance():
        if TimeseriesPersistenceService.__instance is None:
            TimeseriesPersistenceService()
        return TimeseriesPersistenceService.__instance

    def __init__(self):
        if TimeseriesPersistenceService.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        TimeseriesPersistenceService.__instance = self

        self.bucket = cfg.config['influx2']['default_bucket']

        # Directly use the config file through the influx API
        self.__client: InfluxDBClient = InfluxDBClient.from_config_file(config_file='sindit.cfg')

        # Synchronous mode to allow live data processing from the database
        # Consider batch mode if having performance issues
        self.__write_api = self.__client.write_api(write_options=SYNCHRONOUS)
        self.__query_api = self.__client.query_api()

    def test_influx_connection(self):
        test_record = Point("test_measurement").tag("test_tag", "test_tag_value").field("test_field", 17)
        self.__write_api.write(bucket=self.bucket, record=test_record)

        print("influx test written")

        ## using Table structure
        tables = self.__query_api.query(f'from(bucket:"{self.bucket}") |> range(start: -10m)')

        for table in tables:
            print(table)
            for row in table.records:
                print(row.values)

    def write_measurement(self,
                          id_uri: str,
                          reading_time: datetime,
                          value):
        record = Point(measurement_name=id_uri)\
            .field(field='reading', value=value)
        self.__write_api.write(bucket=self.bucket, record=record)
