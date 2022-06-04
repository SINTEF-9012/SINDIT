import json
from datetime import datetime

from sensor_inputs.SensorInput import SensorInput


class MqttSensorInput(SensorInput):

    def __init__(self,
                 topic,
                 json_keyword,
                 timestamp_json_keyword='ts'
                 ):
        # TODO: change ID name to global identifier / URI?
        super(MqttSensorInput, self).__init__(id_name=f"MQTT-{topic}-{json_keyword}")
        self.json_keyword = json_keyword
        self.timestamp_json_keyword = timestamp_json_keyword
        self.topic = topic

    def handle_raw_reading(self, payload):
        parsed_json = json.loads(payload)
        timestamp_string = parsed_json.get(self.timestamp_json_keyword)
        timestamp = datetime.strptime(timestamp_string, '%Y-%m-%dT%H:%M:%S.%fZ')
        self.handle_reading(reading_time=timestamp, reading_value=parsed_json.get(self.json_keyword))