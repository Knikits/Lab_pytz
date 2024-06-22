import json
import unittest
from app import application

class TestApp(unittest.TestCase):
    def setUp(self):
        self.environ = {
            'wsgi.input': None,
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
            'CONTENT_LENGTH': '0',
        }
    def test_get_root(self):
        self.environ['PATH_INFO'] = '/'
        response = self.start_response_wrapper(self.environ)
        self.assertEqual(response[0], '200 OK')
        self.assertIn('Current time in GMT', response[1].decode('utf-8'))
    def test_post_convert(self):
        self.environ['REQUEST_METHOD'] = 'POST'
        self.environ['PATH_INFO'] = '/api/v1/convert'
        data = {
            'date': '12.20.2021 22:21:05',
            'tz': 'EST',
            'target_tz': 'Europe/Moscow'
        }
        self.environ['wsgi.input'] = io.BytesIO(json.dumps(data).encode('utf-8'))
        self.environ['CONTENT_LENGTH'] = str(len(json.dumps(data)))
        response = self.start_response_wrapper(self.environ)
        self.assertEqual(response[0], '200 OK')
        response_data = json.loads(response[1].decode('utf-8'))
        self.assertIn('converted_time', response_data)
    def test_post_datediff(self):
        self.environ['REQUEST_METHOD'] = 'POST'
        self.environ['PATH_INFO'] = '/api/v1/datediff'
        data = {
            'first_date': '12.06.2024 22:21:05',
            'first_tz': 'EST',
            'second_date': '12:30pm 2024-02-01',
            'second_tz': 'Europe/Moscow'
        }
        self.environ['wsgi.input'] = io.BytesIO(json.dumps(data).encode('utf-8'))
        self.environ['CONTENT_LENGTH'] = str(len(json.dumps(data)))
        response = self.start_response_wrapper(self.environ)
        self.assertEqual(response[0], '200 OK')
        response_data = json.loads(response[1].decode('utf-8'))
        self.assertIn('difference_seconds', response_data)
    def start_response_wrapper(self, environ):
        def start_response(status, headers):
            self.status = status
            self.headers = headers

        result = application(environ, start_response)
        return self.status, b''.join(result)