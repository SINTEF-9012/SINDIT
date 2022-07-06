import abc
from datetime import datetime
import pandas as pd

from service.specialized_databases.SpecializedDatabasePersistenceService import (
    SpecializedDatabasePersistenceService,
)


class TimeseriesPersistenceService(SpecializedDatabasePersistenceService):
    """
    Persistence service for timeseries data
    """

    @abc.abstractmethod
    def write_measurement(
        self, id_uri: str, value: float | bool | str, reading_time: datetime = None
    ):
        """
        Writes the given value to the standard bucket into the measurement according to the id_uri into a field
        called 'reading'.
        When no reading time is given, the current database time is being used.
        :param id_uri:
        :param value:
        :param reading_time:
        :return:
        """
        pass

    @abc.abstractmethod
    def read_period_to_dataframe(
        self,
        id_uri: str,
        begin_time: datetime,
        end_time: datetime,
        aggregation_window_ms: int | None,
    ) -> pd.DataFrame:
        """
        Reads all measurements from the sensor with the given ID in the time period
        :param id_uri:
        :param begin_time:
        :param end_time:
        :return: Dataframe containing all measurements in that period
        :raise IdNotFoundException: if the id_uri is not found
        """
        pass

    @abc.abstractmethod
    def count_entries_for_period(
        self, id_uri: str, begin_time: datetime, end_time: datetime
    ) -> int:
        """
        Counts the measurement entries from the sensor with the given ID in the time period
        :param id_uri:
        :param begin_time:
        :param end_time:
        :return: number of entries
        :raise IdNotFoundException: if the id_uri is not found
        """
        pass
