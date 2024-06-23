import unittest
from wsgiref.validate import validator
from wsgiref.simple_server import make_server
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import json
import threading
from app import application

class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server('', 2280, validator(application))
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.start()
        
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()

    def fetch_response(self, url, data=None, method='GET'):
        request = Request(url, data=data, method=method)
        return urlopen(request)
    
    def test_get_gmt_time(self):
        response = self.fetch_response('http://localhost:2280/')
        self.assertEqual(response.status, 200)
        self.assertIn(b'Current time in GMT', response.read())

    def test_get_specific_timezone(self):
        response = self.fetch_response('http://localhost:2280/Asia/Tel_Aviv')
        self.assertEqual(response.status, 200)
        self.assertIn(b'Current time in Asia/Tel_Aviv', response.read())
        
    def test_convert_timezone(self):
        data = json.dumps({
            "date": "06.15.2024 22:21:05",
            "tz": "EST",
            "target_tz": "Asia/Ho_Chi_Minh"
        }).encode('utf-8')
        response = self.fetch_response('http://localhost:2280/api/v1/convert', data=data, method='POST')
        self.assertEqual(response.status, 200)
        result = json.loads(response.read())
        self.assertIn('converted_date', result)

    def test_date_difference(self):
        data = json.dumps({
            "first_date": "06.15.2024 22:21:05", 
            "first_tz": "CET", 
            "second_date": "12:30pm 2024-06-15", 
            "second_tz": "US/Hawaii"
        }).encode('utf-8')
        response = self.fetch_response('http://localhost:2280/api/v1/datediff', data=data, method='POST')
        self.assertEqual(response.status, 200)
        result = json.loads(response.read())
        self.assertIn('seconds_difference', result)
    
    def test_invalid_timezone(self):
        with self.assertRaises(HTTPError) as cm:
            self.fetch_response('http://localhost:2280/Invalid/Timezone')
        self.assertEqual(cm.exception.code, 404)
        self.assertIn(b'Timezone not found', cm.exception.read())

if __name__ == '__main__':
    unittest.main()