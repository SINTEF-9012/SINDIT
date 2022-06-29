from datetime import datetime
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point
import pandas as pd

from config import global_config as cfg
from graph_domain.DatabaseConnection import DatabaseConnection
from service.exceptions.IdNotFoundException import IdNotFoundException
from service.specialized_databases.timeseries.TimeseriesPersistenceService import (
    TimeseriesPersistenceService,
)

READING_FIELD_NAME = "reading"


class InfluxDbPersistenceService(TimeseriesPersistenceService):
    """ """

    @classmethod
    def instance(cls):
        # if cls.__instance is None:
        #     cls()
        # return cls.__instance
        pass

    # TODO: remove

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bucket = self.group

        self._client: InfluxDBClient = InfluxDBClient(
            url=self.host + ":" + self.port,
            # url="http://sindit-influx-db:8086",
            token=self.key,
            org=self.database,
            verify_ssl=self.key is not None,
        )

        # # Directly use the config file through the influx API
        # self.__client: InfluxDBClient = InfluxDBClient.from_config_file(
        #     config_file=cfg.PATH_TO_CONFIG
        # )
        # TODO: remove

        # Synchronous mode to allow live data processing from the database
        # Consider batch mode if having performance issues
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
        self._query_api = self._client.query_api()

    # override
    def write_measurement(self, id_uri: str, value, reading_time: datetime = None):
        """
        Writes the given value to the standard bucket into the measurement according to the id_uri into a field
        called 'reading'.
        When no reading time is given, the current database time is being used.
        :param id_uri:
        :param value:
        :param reading_time:
        :return:
        """

        record = Point(measurement_name=id_uri).field(
            field=READING_FIELD_NAME, value=value
        )
        if reading_time is not None:
            record.time(reading_time)
        self._write_api.write(bucket=self.bucket, record=record)

    # override
    def read_period_to_dataframe(
        self, id_uri: str, begin_time: datetime, end_time: datetime
    ) -> pd.DataFrame:
        """
        Reads all measurements from the sensor with the given ID in the time period
        :param id_uri:
        :param begin_time:
        :param end_time:
        :return: Dataframe containing all measurements in that period
        :raise IdNotFoundException: if the id_uri is not found
        """
        query = (
            f'from(bucket: "{self.bucket}")\n'
            f"|> range(start: {begin_time.astimezone().isoformat()}, stop: {end_time.astimezone().isoformat()})\n"
            f'|> filter(fn: (r) => r["_measurement"] == "{id_uri}")'
            f'|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\n'
            f'|> keep(columns: ["_time", "{READING_FIELD_NAME}"])'
        )

        try:
            df = self._query_api.query_data_frame(query=query)

            # Dataframe cleanup
            df.drop(columns=["result", "table"], axis=1, inplace=True)
            df.rename(
                columns={"_time": "time", READING_FIELD_NAME: "value"}, inplace=True
            )

            return df

        except KeyError:
            # id_uri not found
            raise IdNotFoundException
