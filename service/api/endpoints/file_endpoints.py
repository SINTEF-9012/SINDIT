import json
from datetime import datetime, timedelta
import pandas as pd
from fastapi.responses import StreamingResponse


from service.api.api import app
from service.exceptions.IdNotFoundException import IdNotFoundException
from service.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from service.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from service.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from service.specialized_databases.files.FilesPersistenceService import (
    FilesPersistenceService,
)
from service.specialized_databases.timeseries.TimeseriesPersistenceService import (
    TimeseriesPersistenceService,
)
from service.specialized_databases.timeseries.influx_db.InfluxDbPersistenceService import (
    InfluxDbPersistenceService,
)


DB_SERVICE_CONTAINER: DatabasePersistenceServiceContainer = (
    DatabasePersistenceServiceContainer.instance()
)
DB_CON_NODE_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()


@app.get("/supplementary_file")
def get_supplementary_file(iri: str):
    """
    Reads the specified file from the file storage
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """

    try:
        # Get related timeseries-database service:
        file_con_node: DatabaseConnectionsDao = (
            DB_CON_NODE_DAO.get_database_connection_for_node(iri)
        )

        if file_con_node is None:
            print("File requested, but database connection node does not exist")
            return None

        file_service: FilesPersistenceService = (
            DB_SERVICE_CONTAINER.get_persistence_service(file_con_node.iri)
        )

        # Read the actual file:
        file_stream = file_service.read_file(
            iri=iri,
        )

        return StreamingResponse(
            file_stream.iter_chunks(),
            media_type="file",
        )

    except IdNotFoundException:
        return None
