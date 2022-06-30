import json
from datetime import datetime

from service.runtime_connections.TimeseriesInput import TimeseriesInput

TIMESTAMP_JSON_KEYWORD = "ts"


class MqttTimeseriesInput(TimeseriesInput):
    def handle_raw_reading(self, payload):
        parsed_json = json.loads(payload)
        timestamp_string = parsed_json.get(TIMESTAMP_JSON_KEYWORD)
        timestamp = datetime.strptime(timestamp_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        self.handle_reading(
            reading_time=timestamp,
            reading_value=parsed_json.get(self.connection_keyword),
        )
