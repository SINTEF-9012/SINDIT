import abc

from typing import List

from service.runtime_connections.TimeseriesInput import TimeseriesInput


class SensorConnection(abc.ABC):
    """
    Base class for sensor connections (OPCUA, MQTT, ...)
    One or several sensor inputs can be available via one connection over different
    topics.
    """

    def __init__(self, inputs: List[TimeseriesInput]):
        """
        Creates a new MQTT connection
        :param inputs: single inputs available over this connection
        """
        # this could be later changed to a dict to enable faster resolving given the id / topic..
        self.sensor_inputs = inputs

    @abc.abstractmethod
    def start_connection(self):
        pass
