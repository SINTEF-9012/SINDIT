import json
from datetime import datetime, timedelta
import pandas as pd
from fastapi.responses import StreamingResponse
from fastapi.responses import RedirectResponse


from service.api.api import app
from service.exceptions.IdNotFoundException import IdNotFoundException
from service.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from service.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from service.knowledge_graph.dao.SupplementaryFileNodesDao import (
    SupplementaryFileNodesDao,
)
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
from service.knowledge_graph.dao.AssetNodesDao import AssetsDao


DB_SERVICE_CONTAINER: DatabasePersistenceServiceContainer = (
    DatabasePersistenceServiceContainer.instance()
)
DB_CON_NODE_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()
SUPPL_FILE_DAO: SupplementaryFileNodesDao = SupplementaryFileNodesDao.instance()


@app.get("/supplementary_file/data")
def get_supplementary_file(iri: str, proxy_mode: bool = False):
    """
    Reads the specified file from the file storage
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    if proxy_mode:
        return get_supplementary_file_proxy_mode(iri)
    else:
        return get_supplementary_file_redirect(iri)


def get_supplementary_file_proxy_mode(iri: str):

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
        file_stream = file_service.stream_file(
            iri=iri,
        )

        stream = StreamingResponse(
            file_stream.iter_chunks(), media_type="application/octet-stream"
        )

        return stream

    except IdNotFoundException:
        return None


def get_supplementary_file_redirect(iri: str):

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

        # Create the temporary redirect link:
        redirect_url = file_service.get_temp_file_url(
            iri=iri,
        )

        return RedirectResponse(redirect_url)

        # stream = StreamingResponse(
        #     file_stream.iter_chunks(), media_type="application/octet-stream"
        # )

        # return stream

    except IdNotFoundException:
        return None


@app.get("/supplementary_file/details")
def get_supplementary_file(iri: str):
    """
    Reads the details (e.g. type and file-name) for a supplementary file from the graph
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    return SUPPL_FILE_DAO.get_supplementary_file_node_flat(iri)
