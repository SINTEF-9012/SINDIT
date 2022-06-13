import abc
from datetime import datetime


class SensorInput(abc.ABC):

    def __init__(self, id_uri: str):
        self._last_reading: (datetime, float) = None
        self._handlers = []
        self.id_uri = id_uri

    def get_most_current(self) -> (datetime, float):
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
        for handler in self._handlers:
            handler(self.id_uri, reading_value, reading_time)
        self._last_reading = reading_time, reading_value
        # print(f"Sensor {self.id_uri} updated: {self.get_most_current()}")
