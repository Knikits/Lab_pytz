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

def date_diff(first_date_str, first_tz_str, second_date_str, second_tz_str):
    first_tz = pytz.timezone(first_tz_str)
    second_tz = pytz.timezone(second_tz_str)
    first_date = datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S')
    second_date = datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d')
    first_time = first_tz.localize(first_date)
    second_time = second_tz.localize(second_date)
    diff = second_time - first_time
    return diff.total_seconds()

def application(environ, start_response):