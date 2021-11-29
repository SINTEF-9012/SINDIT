"""
Interact w/ InfluxDB (<=1.8).

History:
- 11 Dec 2020, Maryna Waszak <maryna.waszak@sintef.no>, batch store of values now possible
- 08 Dec 2020, Volker Hoffmann <volker.hoffmann@sintef.no>, Cleanup, Add Query
- 07 Dec 2020, Nikolay Nikolov <nikolay.nikolov@sintef.no>, More Generic API
- 18 Nov 2020, Nikolay Nikolov <nikolay.nikolov@sintef.no>, Initial Commit
"""

from influxdb import InfluxDBClient
import configparser
import pandas as pd
import environment.settings as stngs

class DTPrototypeInfluxDbClient:
    def __init__(self, path_to_config='sindit.cfg'):
        config = configparser.ConfigParser()
        config.read(path_to_config)

        self.host = stngs.INFLUXDB_URI
        self.port_number = stngs.INFLUXDB_PORT
        self.username = config['influxdb']['influx_user'] or 'root'
        self.password = config['influxdb']['influx_pass'] or 'root'
        self.db_name = config['influxdb']['db_name']
        self.batch_size = config['influxdb']['write_batch_size']

        self.client = InfluxDBClient(host=self.host, port=self.port_number, username=self.username, password=self.password)
        if {'name': self.db_name} not in self.client.get_list_database():
            self.client.create_database(self.db_name)
    

    def store_any_measurement(self, measurement_type, tags, measurement_values, measurement_times):
        """writes measurements to influxdb.

        :param measurement_type: string describing the measurement e.g., 'temperature','vibration'
        :type measurement_type: str

        :param tags: a set of key-value pairs associated with each point. Both
            keys and values must be strings. These are shared tags and will be
            merged with point-specific tags, defaults to None           
        :type tags: dict
        
        :param measurement_values: list of values or single number
        :type database: list, number
              
        :param measurement_times: list of time tags as int epoch from time() in milliseconds
        :type retention_policy: list of epoch ints or a single epoch in ms
        
        :returns: True, if the operation is successful
        :rtype: bool

        .. note:: no defaults
        """  
        
        data = []
        # create tag value-pairs from input dictionary
        tag_value_pairs = ""
        for kk, (tag, value) in enumerate(tags.items()):
            tag_value_pairs += tag + "=" + value
            if kk < len(tags)-1: # if not last - add comma between them
                tag_value_pairs += ','
        
        # if only one measurement then we need to make them iterable to create data blob
        if isinstance(measurement_times, int):
                measurement_times = [measurement_times]
                measurement_values = [measurement_values]
        
        # iterate through measurement lists and create a dict to write to influxdb
        try:
            for idx, el in enumerate(measurement_values):
                data.append("{measurement},{tag_value_pairs} value={measurement_value} {timestamp}"
                    .format(measurement = measurement_type,
                            tag_value_pairs = tag_value_pairs,
                            measurement_value = el,
                            timestamp=int(measurement_times[idx])))
        except TypeError:
            print("Could not iterate through measurement_values.")
            return False
        
        self.client.write_points(data, database=self.db_name, time_precision='ms', protocol='line', batch_size=int(self.batch_size), retention_policy='autogen')

        return True

    def get_any_measurement_as_dataframe(self, \
                                        measurement_type='temperature', \
                                        tags={ 'machine': 'M1', \
                                               'sensor': 'S1_1' } ):

        # query = "SELECT * "
        # query += "FROM \"%s\" " % measurement_type
        # query += "WHERE machine = '%s' " % machine
        # query += "AND sensor = '%s' " % sensor
        # query += "ORDER BY time ASC"

        query = "SELECT * "
        query += "FROM \"%s\" " % measurement_type
        for kk, (tag, value) in enumerate(tags.items()):
            if kk == 0:
                query += "WHERE %s = '%s' " % (tag, value)
            else:
                query += "AND %s = '%s' " % (tag, value)
        query += "ORDER BY time ASC"
        result = self.client.query(query, database=self.db_name)

        timestamps = []
        values = []
        for pt in result.get_points():
            timestamps.append(pt['time'])
            values.append(pt['value'])
        df = pd.DataFrame(data={'timestamp': pd.to_datetime(timestamps), \
                                "%s" % measurement_type: values})
        return df
