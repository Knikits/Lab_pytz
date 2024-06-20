import json
import pytz
from datetime import datetime
from wsgiref.simple_server import make_server

def get_time_in_timezone(tz_name='GMT'):
    try:
        tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        tz = pytz.timezone('GMT')
    now = datetime.now(tz)
    return now.strftime('%Y-%m-%d %H:%M:%S %Z%z')

def convert_time(date_str, source_tz_str, target_tz_str):
    source_tz = pytz.timezone(source_tz_str)
    target_tz = pytz.timezone(target_tz_str)
    date = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S')
    source_time = source_tz.localize(date)
    target_time = source_time.astimezone(target_tz)
    return target_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')