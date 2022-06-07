import json
from datetime import datetime

from service.sensor_inputs.SensorInput import SensorInput


class MqttSensorInput(SensorInput):

    def __init__(self,
                 id_uri: str,
                 topic: str,
                 json_keyword: str,
                 timestamp_json_keyword='ts'
                 ):
        super(MqttSensorInput, self).__init__(id_uri=id_uri)
        self.json_keyword = json_keyword
        self.timestamp_json_keyword = timestamp_json_keyword
        self.topic = topic

    def handle_raw_reading(self, payload):
        parsed_json = json.loads(payload)
        timestamp_string = parsed_json.get(self.timestamp_json_keyword)
        timestamp = datetime.strptime(timestamp_string, '%Y-%m-%dT%H:%M:%S.%fZ')
        self.handle_reading(reading_time=timestamp, reading_value=parsed_json.get(self.json_keyword))
