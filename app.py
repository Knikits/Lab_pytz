import json
import pytz
from datetime import datetime
from wsgiref.simple_server import make_server

def get_current_time_response(tz_name):
    try:
        timezone = pytz.timezone(tz_name)
        current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        response_body = f'<html><body><h1>Current time in {tz_name}: {current_time}</h1></body></html>'
        return '200 OK', 'text/html', response_body
    except pytz.UnknownTimeZoneError:
        available_timezones = '\n'.join(pytz.all_timezones)
        response_body = f'<html><body><h1>Timezone not found</h1><pre>{available_timezones}</pre></body></html>'
        return '404 Not Found', 'text/html', response_body

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
    path = environ.get('PATH_INFO', '')
    method = environ.get('REQUEST_METHOD', 'GET')

    if method == 'GET' and path.startswith('/'):
        tz_name = path[1:] or 'GMT'
        response_body = f"<html><body>Current time in {tz_name}: {get_time_in_timezone(tz_name)}</body></html>"
        status = '200 OK'
        headers = [('Content-type', 'text/html; charset=utf-8')]

    elif method == 'POST' and path == '/api/v1/convert':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)

            date_str = data['date']
            source_tz = data['tz']
            target_tz = data['target_tz']

            converted_time = convert_time(date_str, source_tz, target_tz)

            response_body = json.dumps({"converted_time": converted_time})
            status = '200 OK'
            headers = [('Content-type', 'application/json; charset=utf-8')]
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
            status = '400 Bad Request'
            headers = [('Content-type', 'application/json; charset=utf-8')]

    elif method == 'POST' and path == '/api/v1/datediff':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)

            first_date = data['first_date']
            first_tz = data['first_tz']
            second_date = data['second_date']
            second_tz = data['second_tz']

            diff_seconds = date_diff(first_date, first_tz, second_date, second_tz)

            response_body = json.dumps({"difference_seconds": diff_seconds})
            status = '200 OK'
            headers = [('Content-type', 'application/json; charset=utf-8')]
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
            status = '400 Bad Request'
            headers = [('Content-type', 'application/json; charset=utf-8')]

    else:
        response_body = json.dumps({"error": "Invalid request"})
        status = '404 Not Found'
        headers = [('Content-type', 'application/json; charset=utf-8')]

    start_response(status, headers)
    return [response_body.encode('utf-8')]

if __name__ == '__main__':
    with make_server('', 4800, application) as httpd:
        print("Serving on port 4800...")
        httpd.serve_forever()