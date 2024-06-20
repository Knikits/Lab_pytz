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