import json
from datetime import datetime, timedelta
import pandas as pd

from service.api.api import app
from config import global_config as cfg
from service.exceptions.IdNotFoundException import IdNotFoundException
from service.timeseries_persistence.TimeseriesPersistenceService import TimeseriesPersistenceService

TS_SERVICE: TimeseriesPersistenceService = TimeseriesPersistenceService.instance()

@app.get("/sensors/current_timeseries")
def get_current_timeseries(sensor_id_uri: str):
    try:
        df = TS_SERVICE.read_period_to_dataframe(
            id_uri=sensor_id_uri,
            begin_time=datetime.now() - timedelta(seconds=cfg.get_int(
                group=cfg.ConfigGroups.API,
                key='current_timeseries_duration')),
            end_time=datetime.now()
        )

        return df.to_json(date_format='iso')
    except IdNotFoundException:
        return pd.DataFrame(columns=['time', 'value'])
