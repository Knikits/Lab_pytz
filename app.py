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

def convert_timezone(data):
    try:
        date_str = data['date']
        source_tz = data['tz']
        target_tz = data['target_tz']
        
        source_timezone = pytz.timezone(source_tz)
        target_timezone = pytz.timezone(target_tz)
        
        naive_date = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S')
        source_date = source_timezone.localize(naive_date)
        target_date = source_date.astimezone(target_timezone)
        
        response = {'converted_date': target_date.strftime('%Y-%m-%d %H:%M:%S')}
        return '200 OK', 'application/json', json.dumps(response)
    except Exception as e:
        return '400 Bad Request', 'application/json', json.dumps({'error': str(e)})

def date_difference(data):
    try:
        first_date_str = data['first_date']
        first_tz = data['first_tz']
        second_date_str = data['second_date']
        second_tz = data['second_tz']
        
        first_timezone = pytz.timezone(first_tz)
        second_timezone = pytz.timezone(second_tz)
        
        naive_first_date = datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S')
        naive_second_date = datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d')
        
        first_date = first_timezone.localize(naive_first_date)
        second_date = second_timezone.localize(naive_second_date)
        
        date_diff = (second_date - first_date).total_seconds()
        
        response = {'seconds_difference': date_diff}
        return '200 OK', 'application/json', json.dumps(response)
    except Exception as e:
        return '400 Bad Request', 'application/json', json.dumps({'error': str(e)})

def application(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/')
    method = environ.get('REQUEST_METHOD')

    if method == 'GET':
        tz_name = path if path else 'GMT'
        status, content_type, response_body = get_current_time_response(tz_name)
    elif method == 'POST':
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(request_body_size)
        data = json.loads(request_body)
        
        if path == 'api/v1/convert':
            status, content_type, response_body = convert_timezone(data)
        elif path == 'api/v1/datediff':
            status, content_type, response_body = date_difference(data)
        else:
            status, content_type, response_body = '404 Not Found', 'text/html', 'Page not found'
    else:
        status, content_type, response_body = '404 Not Found', 'text/html', 'Page not found'
    
    start_response(status, [('Content-Type', content_type)])
    return [response_body.encode('utf-8')]

if __name__ == '__main__':
    httpd = make_server('', 2280, application)
    print("Serving on port 2280...")
    httpd.serve_forever()