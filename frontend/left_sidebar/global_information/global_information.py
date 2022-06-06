import datetime

import dash_bootstrap_components as dbc
import requests
from dash import html

import environment.settings as stngs

API_URI = stngs.FAST_API_URI


def get_layout():
    time_now = datetime.datetime.now()
    shift_end = time_now.replace(hour=19, minute=30)
    remaining_work_time = (shift_end - time_now)
    if remaining_work_time.total_seconds() < 0:
        remaining_work_time = datetime.timedelta(0)

    def reformat_delta_time(delta):
        ms = delta.microseconds // 1000
        sec = delta.seconds
        hours = sec // 3600
        minutes = (sec // 60) - (hours * 60)
        seconds = sec - (minutes * 60) - (hours * 60)
        new_format = str(hours) + ' h ' + str(minutes) + ' min'
        if hours == 0 and minutes == 0:
            new_format = str(seconds) + ' sec'
        if sec == 0:
            new_format = str(ms) + ' msec'
        return new_format

    rows = []
    header_style = {'color': 'black', 'fontSize': 14, 'font-weight': 'bold'}
    rows.append(html.Tr([html.Td("TIMES [hh:mm]", style=header_style), html.Td()]))
    rows.append(html.Tr([html.Td("Current Time"), html.Td(time_now.strftime("%H:%M"))]))
    rows.append(html.Tr([html.Td("Shift ends at"), html.Td(shift_end.strftime("%H:%M"))]))
    rows.append(html.Tr([html.Td("Remaining time"), html.Td(reformat_delta_time(remaining_work_time))]))
    rows.append(html.Tr([html.Td(), html.Td()]))

    # we know that P10.1 is the last process in the production before the exit node
    # @todo: look for the specific process before the exit buffers
    last_arr_time = requests.get(API_URI + '/get_last_prod_arrival_time_from_influxDB/' + 'M5').json()
    avg_arr_time = requests.get(API_URI + '/get_avg_arrival_freq_from_influxDB/' + 'M5').json()
    rows.append(html.Tr([html.Td("PARTS ARRIVAL [hh:mm]", style=header_style), html.Td()]))
    avg_arr_time_str = 'not available'
    last_arr_time_str = 'not available'
    if not isinstance(avg_arr_time, str):
        avg_arr_time = datetime.timedelta(milliseconds=avg_arr_time)
        avg_arr_time_str = reformat_delta_time(avg_arr_time)
        last_arr_time_str = last_arr_time

    rows.append(html.Tr([html.Td("Avg. arrival duration"), html.Td(avg_arr_time_str)]))
    rows.append(html.Tr([html.Td("Last product arrived at"), html.Td(last_arr_time_str)]))
    rows.append(html.Tr([html.Td(), html.Td()]))

    parts = requests.get(API_URI + '/get_exit_parts/').json()
    planned_amount = 150
    rows.append(html.Tr([html.Td("TOTAL AMOUNT [pieces]", style=header_style), html.Td()]))
    rows.append(html.Tr([html.Td("Planned amount"), html.Td(planned_amount)]))
    rows.append(html.Tr([html.Td("Ammount left on remaining time"), html.Td(planned_amount - len(parts))]))
    rows.append(html.Tr([html.Td(), html.Td()]))

    # constantly run a fast simulation to do this estimate
    sim_time = int(remaining_work_time.total_seconds())
    response = None  # requests.get(API_URI+'/get_sim_prediction_from_neo4j/'+str(sim_time))
    try:
        sim_results = response.json()
        parts_est = sim_results[0]['num_of_parts']
    except:
        parts_est = 'not available'
    rows.append(html.Tr([html.Td("ESTIMATED AMOUNT BY SHIFT END", style=header_style), html.Td(parts_est)]))
    rows.append(html.Tr([html.Td(), html.Td()]))

    rows.append(html.Tr([html.Td("CURRENT AMOUNT", style=header_style), html.Td(len(parts))]))
    table_body = [html.Tbody(rows)]

    table = dbc.Table(table_body, id='live-update-table-text', bordered=False)

    return table
