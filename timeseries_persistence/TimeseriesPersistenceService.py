from datetime import datetime
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point
import pandas as pd

from config import global_config as cfg
from exceptions.IdNotFoundException import IdNotFoundException

READING_FIELD_NAME = 'reading'


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
        self.__client: InfluxDBClient = InfluxDBClient.from_config_file(config_file=cfg.PATH_TO_CONFIG)

        # Synchronous mode to allow live data processing from the database
        # Consider batch mode if having performance issues
        self.__write_api = self.__client.write_api(write_options=SYNCHRONOUS)
        self.__query_api = self.__client.query_api()

    def test_influx_connection(self):
        test_record = Point("test_measurement").tag("test_tag", "test_tag_value").field("test_field", 17)
        self.__write_api.write(bucket=self.bucket, record=test_record)

        print("influx test written")

        # using Table structure
        tables = self.__query_api.query(f'from(bucket:"{self.bucket}") |> range(start: -10m)')

        for table in tables:
            print(table)
            for row in table.records:
                print(row.values)

    def write_measurement(self,
                          id_uri: str,
                          value,
                          reading_time: datetime = None
                          ):
        """
        Writes the given value to the standard bucket into the measurement according to the id_uri into a field
        called 'reading'.
        When no reading time is given, the current database time is being used.
        :param id_uri:
        :param value:
        :param reading_time:
        :return:
        """

        record = Point(measurement_name=id_uri) \
            .field(field=READING_FIELD_NAME, value=value)
        if reading_time is not None:
            record.time(reading_time)
        self.__write_api.write(bucket=self.bucket, record=record)

    def read_period_to_dataframe(self,
                                 id_uri: str,
                                 begin_time: datetime,
                                 end_time: datetime
                                 ) -> pd.DataFrame:
        """
        Reads all measurements from the sensor with the given ID in the time period
        :param id_uri:
        :param begin_time:
        :param end_time:
        :return: Dataframe containing all measurements in that period
        :raise IdNotFoundException: if the id_uri is not found
        """
        query = f'from(bucket: "{self.bucket}")\n' \
                f'|> range(start: {begin_time.astimezone().isoformat()}, stop: {end_time.astimezone().isoformat()})\n' \
                f'|> filter(fn: (r) => r["_measurement"] == "{id_uri}")' \
                f'|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\n' \
                f'|> keep(columns: ["_time", "{READING_FIELD_NAME}"])'

        try:
            df = self.__query_api.query_data_frame(query=query)

            # Dataframe cleanup
            df.drop(columns=["result", "table"], axis=1, inplace=True)
            df.rename(columns={"_time": "time", READING_FIELD_NAME: "value"}, inplace=True)

            return df

        except KeyError:
            # id_uri not found
            raise IdNotFoundException
