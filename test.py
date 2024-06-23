import unittest # to create and execute tests
from wsgiref.validate import validator
from wsgiref.simple_server import make_server
from urllib.request import urlopen, Request
from urllib.error import HTTPError # to handle HTTP errors
import json
import threading # to work with streams
from app import application # import WSGI application

class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server('', 2280, validator(application))
        cls.thread = threading.Thread(target=cls.server.serve_forever) # create a thread to start the server
        cls.thread.start()
        
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown() # stop the server
        cls.thread.join()

    def fetch_response(self, url, data=None, method='GET'):
        request = Request(url, data=data, method=method) # create a request with the specified URL, data and method
        return urlopen(request)
    
    def test_get_gmt_time(self):
        response = self.fetch_response('http://localhost:2280/') # send a GET request to the home page
        self.assertEqual(response.status, 200) 
        self.assertIn(b'Current time in GMT', response.read()) # check that the response contains a string with the current time in GMT

    def test_get_specific_timezone(self):
        response = self.fetch_response('http://localhost:2280/Asia/Tel_Aviv')  # send GET request to page with time zone Asia/Tel_Aviv
        self.assertEqual(response.status, 200)
        self.assertIn(b'Current time in Asia/Tel_Aviv', response.read()) # check that the response contains a string with the current time in Asia/Tel_Aviv
        
    def test_convert_timezone(self):
        data = json.dumps({
            "date": "06.15.2024 22:21:05",
            "tz": "EST",
            "target_tz": "Asia/Ho_Chi_Minh"
        }).encode('utf-8') 
        response = self.fetch_response('http://localhost:2280/api/v1/convert', data=data, method='POST') # send POST request for API time zone conversions
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
        response = self.fetch_response('http://localhost:2280/api/v1/datediff', data=data, method='POST') # send POST request for API calculations of the difference between dates
        self.assertEqual(response.status, 200)
        result = json.loads(response.read())
        self.assertIn('seconds_difference', result)
    
    def test_invalid_timezone(self):
        with self.assertRaises(HTTPError) as cm:
            self.fetch_response('http://localhost:2280/Invalid/Timezone') # send GET request with non-existent time zone
        self.assertEqual(cm.exception.code, 404) 
        self.assertIn(b'Timezone not found', cm.exception.read())

if __name__ == '__main__':
    unittest.main() # run the tests