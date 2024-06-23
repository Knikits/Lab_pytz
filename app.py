#   -*- coding: utf-8 -*-
# для комментариев на русском языке

import json # работа с JSON-данными
import pytz # работа с часовыми поясами
from datetime import datetime # работа с датой и временем
from wsgiref.simple_server import make_server # создание WSGI сервера

# по запросу GET /<tz name> отдает текущее время в запрошенной зоне в формате html.
# <tz name> может быть пустым - тогда в GMT
def get_current_time_response(tz_name):
    try:
        timezone = pytz.timezone(tz_name) # объект часового пояса
        current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S') # текущее время в данном часовом поясе, форматирование
        response_body = f'<html><body><h1>Current time in {tz_name}: {current_time}</h1></body></html>'
        return '200 OK', 'text/html', response_body
    except pytz.UnknownTimeZoneError: # если часовой пояс не найден
        available_timezones = '\n'.join(pytz.all_timezones) # список всех доступных часовых поясов
        response_body = f'<html><body><h1>Timezone not found</h1><pre>{available_timezones}</pre></body></html>'
        return '404 Not Found', 'text/html', response_body

# по запросу POST /api/v1/convert - преобразует дату/время из одного часового пояса в другой
# принимает: параметр date - json формата {"date":"12.20.2021 22:21:05", "tz": "EST"}  и target_tz - строку с определением зоны
def convert_timezone(data):
    try:
        date_str = data['date'] # из данных получаем дату
        source_tz = data['tz'] # исходный часовой пояс
        target_tz = data['target_tz'] # заданный пояс
        
        source_timezone = pytz.timezone(source_tz)
        target_timezone = pytz.timezone(target_tz)
        
        naive_date = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S') # преобразуем строку даты в объект datetime
        source_date = source_timezone.localize(naive_date) # локализуем дату в исходном часовом поясе
        target_date = source_date.astimezone(target_timezone) # преобразуем дату в заданный
        
        response = {'converted_date': target_date.strftime('%Y-%m-%d %H:%M:%S')} # ответ с преобразованной датой
        return '200 OK', 'application/json', json.dumps(response)
    except Exception as e: # если возникает ошибка
        return '400 Bad Request', 'application/json', json.dumps({'error': str(e)}) 

# по запросу POST /api/v1/datediff - отдает число секунд между между двумя датами 
# из параметра data (json формат {"first_date":"12.06.2024 22:21:05", "first_tz": "EST", "second_date":"12:30pm 2024-02-01", "second_tz": "Europe/Moscow"})
def date_difference(data):
    try:
        first_date_str = data['first_date']
        first_tz = data['first_tz']
        second_date_str = data['second_date']
        second_tz = data['second_tz']
        
        first_timezone = pytz.timezone(first_tz)
        second_timezone = pytz.timezone(second_tz)
        
        naive_first_date = datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S')  # преобразуем первую строку даты в объект datetime
        naive_second_date = datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d') # преобразуем вторую строку даты в объект datetime
        
        first_date = first_timezone.localize(naive_first_date) # локализуем первую дату в первом часовом поясе
        second_date = second_timezone.localize(naive_second_date) # локализуем вторую дату во втором часовом поясе
        
        date_diff = (second_date - first_date).total_seconds() # вычисляем разницу между датами в секундах
        
        response = {'seconds_difference': date_diff}
        return '200 OK', 'application/json', json.dumps(response)
    except Exception as e:
        return '400 Bad Request', 'application/json', json.dumps({'error': str(e)})

def application(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/') # получаем путь запроса и удаляем начальный слэш
    method = environ.get('REQUEST_METHOD') # получаем метод запроса (GET или POST)

    if method == 'GET':
        tz_name = path if path else 'GMT' # если путь указан, используем его как имя часового пояса, иначе используем GMT
        status, content_type, response_body = get_current_time_response(tz_name) # получаем ответ с текущим временем для указанного часовогг пояса
    elif method == 'POST':
        request_body_size = int(environ.get('CONTENT_LENGTH', 0)) # получаем размер тела запроса
        request_body = environ['wsgi.input'].read(request_body_size) # читаем тело запроса
        data = json.loads(request_body) # парсим JSON-данные из тела запроса
        
        if path == 'api/v1/convert':
            status, content_type, response_body = convert_timezone(data) # выполняем преобразование часового пояса
        elif path == 'api/v1/datediff':
            status, content_type, response_body = date_difference(data) # вычисляем разницу между датами
        else:
            status, content_type, response_body = '404 Not Found', 'text/html', 'Page not found'
    else:
        status, content_type, response_body = '404 Not Found', 'text/html', 'Page not found'
    
    start_response(status, [('Content-Type', content_type)])
    return [response_body.encode('utf-8')]

if __name__ == '__main__':
    httpd = make_server('', 2280, application)  # создаем WSGI сервер на порту 2280
    print("Serving on port 2280...")
    httpd.serve_forever() # запускаем сервер в бесконечном цикле