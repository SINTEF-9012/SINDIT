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
    def read_file(
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
