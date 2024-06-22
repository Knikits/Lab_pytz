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