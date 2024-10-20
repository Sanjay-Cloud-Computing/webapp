import unittest
from unittest.mock import MagicMock
from flask import app
from run import app

class HealthCheckTestCase(unittest.TestCase):

    def setUp(self):
        
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check_with_query_params(self):
       
        response = self.app.get('/healthz?param=value')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.headers['Cache-Control'], 'no-cache, no-store, must-revalidate')

    def test_health_check_with_form_data(self):
        
        response = self.app.get('/healthz', data={'key': 'value'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.headers['Cache-Control'], 'no-cache, no-store, must-revalidate')

    def test_health_check_with_post_request(self):
        
        response = self.app.post('/healthz')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.headers['Cache-Control'], 'no-cache, no-store, must-revalidate')

    def test_invalid_path(self):
       
        response = self.app.get('/invalidpath')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers['Cache-Control'], 'no-cache, no-store, must-revalidate')

if __name__ == '__main__':
    unittest.main()