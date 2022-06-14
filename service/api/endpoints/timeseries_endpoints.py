import json
from datetime import datetime, timedelta
import pandas as pd

from service.api.api import app
from service.exceptions.IdNotFoundException import IdNotFoundException
from service.timeseries_persistence.TimeseriesPersistenceService import TimeseriesPersistenceService

TS_SERVICE: TimeseriesPersistenceService = TimeseriesPersistenceService.instance()

@app.get("/timeseries/current_measurements")
def get_current_timeseries(id_uri: str, duration: float):
    """
    Queries the current measurements for the given duration up to the current time.
    :raises IdNotFoundException: If no data is available for that id at the current time
    :param id_uri:
    :param duration: timespan to query in seconds
    :return:
    """
    try:
        readings_df = TS_SERVICE.read_period_to_dataframe(
            id_uri=id_uri,
            begin_time=datetime.now() - timedelta(seconds=duration),
            end_time=datetime.now()
        )

        return readings_df.to_json(date_format='iso')
    except IdNotFoundException:
        return pd.DataFrame(columns=['time', 'value'])


