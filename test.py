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