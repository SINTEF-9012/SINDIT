import abc
from ctypes.wintypes import BOOL
from datetime import datetime
from typing import Tuple

from graph_domain.TimeseriesNode import TimeseriesNodeFlat, TimeseriesValueTypes


class TimeseriesInput(abc.ABC):
    def __init__(
        self, iri: str, connection_topic: str, connection_keyword: str, value_type: str
    ):
        self._last_reading: Tuple[datetime, float | int | bool | str] = None
        self._handlers = []
        self.iri = iri
        self.connection_topic = connection_topic
        self.connection_keyword = connection_keyword
        self.value_type = value_type

    @classmethod
    def from_timeseries_node(cls, node: TimeseriesNodeFlat):
        return cls(
            iri=node.iri,
            connection_topic=node.connection_topic,
            connection_keyword=node.connection_keyword,
            value_type=node.value_type,
        )

    def get_most_current(self) -> Tuple[datetime, int | float | bool | str]:
        """
        :return: The most current reading with its timestamp
        """
        return self._last_reading

    def register_handler(self, handler_method) -> None:
        """
        Registers a given handler method to be called whenever a reading is being received
        :param handler_method: Callable taking three arguments: id_uri: str, value: Any,
        reading_time: datetime.
        :return: None
        """
        self._handlers.append(handler_method)

    def handle_reading(self, reading_time, reading_value):
        """
        Called whenever a reading is processed. Calls all registered handlers
        :param reading_time:
        :param reading_value:
        :return:
        """
        if self.value_type == TimeseriesValueTypes.STRING.value:
            reading_value = str(reading_value)
        elif self.value_type == TimeseriesValueTypes.DECIMAL.value:
            reading_value = float(reading_value)
        elif self.value_type == TimeseriesValueTypes.INT.value:
            reading_value = int(reading_value)
        elif self.value_type == TimeseriesValueTypes.BOOL.value:
            if isinstance(reading_value, bool):
                pass
            elif isinstance(reading_value, float):
                reading_value = bool(reading_value)
            elif isinstance(reading_value, str):
                reading_value = (
                    reading_value == "True"
                    or reading_value == "true"
                    or reading_value == "t"
                )

        if isinstance(reading_value, str):
            pass

        for handler in self._handlers:
            handler(self.iri, reading_value, reading_time)
        self._last_reading = reading_time, reading_value
