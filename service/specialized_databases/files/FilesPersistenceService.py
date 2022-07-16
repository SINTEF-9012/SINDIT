import abc
from datetime import datetime
import pandas as pd

from service.specialized_databases.SpecializedDatabasePersistenceService import (
    SpecializedDatabasePersistenceService,
)


class FilesPersistenceService(SpecializedDatabasePersistenceService):
    """
    Persistence service for files
    """

    @abc.abstractmethod
    def stream_file(
        self,
        iri: str,
    ):
        """
        Reads
        :param iri:
        :return:
        :raise IdNotFoundException: if the iri is not found
        """
        pass

    @abc.abstractmethod
    def get_temp_file_url(self, iri: str):
        """Creates a temporary URL to directly access the file from S3 without proxying with FastAPI

        Args:
            iri (str): _description_

        Returns:
            _type_: _description_
        """
        pass
