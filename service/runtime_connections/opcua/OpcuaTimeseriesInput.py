from datetime import datetime

from service.runtime_connections.TimeseriesInput import TimeseriesInput


class OpcuaTimeseriesInput(TimeseriesInput):
    def handle_raw_reading(self, val, data):
        # self.handle_reading(reading_time=data.monitored_item.Value.SourceTimestamp, reading_value=val)
        self.handle_reading(reading_time=data.SourceTimestamp, reading_value=val)

    def handle_reading_if_belonging(
        self, node_id: str, reading_time: datetime, value: float
    ):
        if node_id == self.connection_topic:
            self.handle_reading(reading_time=reading_time, reading_value=value)
