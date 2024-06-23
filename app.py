import json
import pytz
from datetime import datetime
from wsgiref.simple_server import make_server

# on GET /<tz name> request gives the current time in the requested zone in html format.
# the <tz name> can be empty - then in GMT
def get_current_time_response(tz_name):
    try:
        timezone = pytz.timezone(tz_name) # time zone object
        current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')  # current time in the given time zone, formatting
        response_body = f'<html><body><h1>Current time in {tz_name}: {current_time}</h1></body></html>'
        return '200 OK', 'text/html', response_body
    except pytz.UnknownTimeZoneError: # if time zone not found
        available_timezones = '\n'.join(pytz.all_timezones) # list of all available time zones
        response_body = f'<html><body><h1>Timezone not found</h1><pre>{available_timezones}</pre></body></html>'
        return '404 Not Found', 'text/html', response_body

# on POST request /api/v1/convert - converts the date/time from one time zone to another.
# accepts: parameter date - json format {"date": "12.20.2021 22:21:05", "tz": "EST"} and target_tz - string with zone definition
def convert_timezone(data):
    try:
        date_str = data['date'] # get the date from the data
        source_tz = data['tz'] # original time zone
        target_tz = data['target_tz'] # set zone
        
        source_timezone = pytz.timezone(source_tz)
        target_timezone = pytz.timezone(target_tz)
        
        naive_date = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S') # convert the date string into a datetime object
        source_date = source_timezone.localize(naive_date) # localise the date in the original time zone
        target_date = source_date.astimezone(target_timezone) # convert the date to a given
        
        response = {'converted_date': target_date.strftime('%Y-%m-%d %H:%M:%S')} # reply with converted date
        return '200 OK', 'application/json', json.dumps(response)
    except Exception as e:
        return '400 Bad Request', 'application/json', json.dumps({'error': str(e)}) 

# by POST /api/v1/datediff - gives the number of seconds between two dates 
# from data parameter (json format {"first_date": "12.06.2024 22:21:05", "first_tz": "EST", "second_date": "12:30pm 2024-02-01", "second_tz": "Europe/Moscow"})
def date_difference(data):
    try:
        first_date_str = data['first_date']
        first_tz = data['first_tz']
        second_date_str = data['second_date']
        second_tz = data['second_tz']
        
        first_timezone = pytz.timezone(first_tz)
        second_timezone = pytz.timezone(second_tz)
        
        naive_first_date = datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S')  # convert the first date string to a datetime object
        naive_second_date = datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d') # convert the second date string to a datetime object
        
        first_date = first_timezone.localize(naive_first_date) # localise the first date in the first time zone
        second_date = second_timezone.localize(naive_second_date) # localise the second date in the second time zone
        
        date_diff = (second_date - first_date).total_seconds() # calculate the difference between the dates in seconds
        
        response = {'seconds_difference': date_diff}
        return '200 OK', 'application/json', json.dumps(response)
    except Exception as e:
        return '400 Bad Request', 'application/json', json.dumps({'error': str(e)})

def application(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/') # get the request path and remove the initial slash
    method = environ.get('REQUEST_METHOD') # get the request method (GET or POST)

    if method == 'GET':
        tz_name = path if path else 'GMT' # if the path is specified, use it as the time zone name, otherwise use GMT
        status, content_type, response_body = get_current_time_response(tz_name) # get a response with the current time for the specified time zone
    elif method == 'POST':
        request_body_size = int(environ.get('CONTENT_LENGTH', 0)) # get the size of the request body
        request_body = environ['wsgi.input'].read(request_body_size) # read the body of the enquiry
        data = json.loads(request_body) # parsing JSON data from the request body
        
        if path == 'api/v1/convert':
            status, content_type, response_body = convert_timezone(data) # perform time zone conversion
        elif path == 'api/v1/datediff':
            status, content_type, response_body = date_difference(data) # calculate the difference between the dates
        else:
            status, content_type, response_body = '404 Not Found', 'text/html', 'Page not found'
    else:
        status, content_type, response_body = '404 Not Found', 'text/html', 'Page not found'
    
    start_response(status, [('Content-Type', content_type)])
    return [response_body.encode('utf-8')]

if __name__ == '__main__':
    httpd = make_server('', 2280, application)  # create a WSGI server on port 2280
    print("Serving on port 2280...")
    httpd.serve_forever() # start the server in an infinite loop