import time
from influxdb_client.client.write_api import  SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point
import global_config as cfg

class TimeseriesPersistenceService(object):
    """

    """

    def __init__(self):
        # url_port = cfg.config['influx_db_timeseries']['host'] + \
        #            cfg.config['influx_db_timeseries']['port']

        # self.__client = InfluxDBClient(
        #     url=url_port,
        #     username=cfg.config['influx_db_timeseries']['user'],
        #     password=cfg.config['influx_db_timeseries']['pw'],
        #     org=cfg.config['influx_db_timeseries']['org'],
        #
        # )

        self.bucket = cfg.config['influx2']['default_bucket']

        # Directly use the config file through the influx API
        self.__client: InfluxDBClient = InfluxDBClient.from_config_file(config_file='sindit.cfg')

        self.__write_api = self.__client.write_api(write_options=SYNCHRONOUS)
        self.__query_api = self.__client.query_api()

        time.sleep(1)

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

