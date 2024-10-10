import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint, request
import sys
def handle_response(status_code):
    return f"Response with status code {status_code}"
 
 
class MockSession:
    def execute(self, query):
        if query == 'SELECT 1':
            return True
        raise Exception("Database Error")
 
    def commit(self):
        pass
 
 
db = MagicMock()
db.session = MockSession()
 
 
health_bp = Blueprint('health_bp', __name__)
 
@health_bp.route('/healthz', methods=['GET'])
def health_check():
    if request.content_length or request.data or request.query_string or request.form:
        return handle_response(400)
    elif request.method in ['GET']:
        try:
            db.session.execute('SELECT 1')
            db.session.commit()
            return handle_response(200)
        except Exception as e:
            return handle_response(503)
    else:
        return handle_response(405)
 
 
class TestHealthCheckEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.app_context().push()
 
    @patch('__main__.handle_response')
    @patch('__main__.db.session.execute')
    def test_health_check_success(self, mock_execute, mock_handle_response):
 
        mock_execute.return_value = True
        mock_handle_response.return_value = "OK"
 
        with self.app.test_request_context('/healthz', method='GET'):
                response = health_check() ## testing here
                mock_execute.assert_called_once_with('SELECT 1')
                mock_handle_response.assert_called_once_with(200)
                self.assertEqual(response, "OK")
 
 
    @patch('__main__.handle_response')
    @patch('__main__.db.session.execute')
    def test_health_check_database_failure(self, mock_execute, mock_handle_response):
 
        mock_execute.side_effect = Exception("Database connection failed")
        mock_handle_response.return_value = "Service Unavailable"
 
        with self.app.test_request_context('/healthz', method='GET'):
            response = health_check()
 
            mock_execute.assert_called_once()
            mock_handle_response.assert_called_once_with(503)
            self.assertEqual(response, "Service Unavailable")
 
    @patch('__main__.handle_response')
    def test_health_check_bad_request(self, mock_handle_response):
        mock_handle_response.return_value = "Bad Request"
 
        with self.app.test_request_context('/healthz', method='GET', data="some data"):
            response = health_check()
            
            mock_handle_response.assert_called_once_with(400)
            self.assertEqual(response, "Bad Request")
    
    @patch('__main__.handle_response')
    def test_health_check_method_not_allowed(self, mock_handle_response):
 
        mock_handle_response.return_value = "Method Not Allowed"
 
        with self.app.test_request_context('/healthz', method='POST'):
            response = health_check()
 
            mock_handle_response.assert_called_once_with(405)
            self.assertEqual(response, "Method Not Allowed")
 
unittest.main(argv=[''], verbosity=2, exit=False)