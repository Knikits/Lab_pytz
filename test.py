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
