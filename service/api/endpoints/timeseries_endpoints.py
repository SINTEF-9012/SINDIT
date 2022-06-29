import json
from datetime import datetime, timedelta
import pandas as pd

from service.api.api import app
from service.exceptions.IdNotFoundException import IdNotFoundException
from service.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from service.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from service.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from service.specialized_databases.timeseries.influx_db.InfluxDbPersistenceService import (
    InfluxDbPersistenceService,
)


DB_SERVICE_CONTAINER: DatabasePersistenceServiceContainer = (
    DatabasePersistenceServiceContainer.instance()
)
DB_CON_NODE_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()


@app.get("/timeseries/current_measurements")
def get_current_timeseries(iri: str, duration: float):
    """
    Queries the current measurements for the given duration up to the current time.
    :raises IdNotFoundException: If no data is available for that id at the current time
    :param id_uri:
    :param duration: timespan to query in seconds
    :return:
    """
    try:
        # Get timeseries-database service:
        ts_con_node = DB_CON_NODE_DAO.get_database_connection_for_node(iri)

        ts_service = DB_SERVICE_CONTAINER.get_persistence_service(ts_con_node.iri)

        # Read the actual measurements:
        readings_df = ts_service.read_period_to_dataframe(
            id_uri=iri,
            begin_time=datetime.now() - timedelta(seconds=duration),
            end_time=datetime.now(),
        )

        return readings_df.to_json(date_format="iso")
    except IdNotFoundException:
        return pd.DataFrame(columns=["time", "value"])
