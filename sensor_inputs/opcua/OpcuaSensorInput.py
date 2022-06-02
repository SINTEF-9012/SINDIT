from datetime import datetime

from sensor_inputs.SensorInput import SensorInput

class OpcuaSensorInput(SensorInput):

    def __init__(self,
                 node_id,
                 ):
        # TODO: change ID name to global identifier / URI?
        super(OpcuaSensorInput, self).__init__(id_name=f"OPC-UA-{node_id}")
        self.node_id = node_id

    def handle_raw_reading(self, val, data):
        # self.handle_reading(reading_time=data.monitored_item.Value.SourceTimestamp, reading_value=val)
        self.handle_reading(reading_time=data.SourceTimestamp, reading_value=val)

    def handle_reading_if_belonging(self, node_id: str, reading_time: datetime, value: float):
        if node_id == self.node_id:
            self.handle_reading(reading_time=reading_time, reading_value=value)

