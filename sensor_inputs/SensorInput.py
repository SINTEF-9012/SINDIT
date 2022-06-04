import abc
from datetime import datetime


class SensorInput(abc.ABC):

    def __init__(self, id_uri: str):
        self._last_reading: (datetime, float) = None
        self._handlers = []
        self.id_uri = id_uri

    def get_most_current(self):
        return self._last_reading

    def register_handler(self, handler_method):
        self._handlers.append(handler_method)

    def handle_reading(self, reading_time, reading_value):
        for handler in self._handlers:
            handler(reading_time, reading_value)
        self._last_reading = reading_time, reading_value
        print(f"Sensor {self.id_uri} updated: {self.get_most_current()}")
