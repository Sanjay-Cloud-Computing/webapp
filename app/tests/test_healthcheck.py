import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, app
from run import app


class HealthCheckTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check_with_query_params(self):
        """Deliberate failure by expecting the wrong status code."""
        # response = self.app.get('/healthz?param=value')
        self.assertEqual(response.status_code, 500, "Deliberate failure: expected status code 500 instead of 400")

    def test_health_check_with_form_data(self):
        """Deliberate failure by expecting incorrect header value."""
        response = self.app.get('/healthz', data={'key': 'value'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.headers['Cache-Control'], 'no-cache', "Deliberate failure: incorrect header value")

    def test_health_check_with_post_request(self):
        """Deliberate failure using self.fail() method."""
        self.fail("Deliberate failure using self.fail() to test CI/CD pipeline")

    def test_invalid_path(self):
        """Original valid test case (kept unchanged for comparison)."""
        response = self.app.get('/invalidpath')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers['Cache-Control'], 'no-cache, no-store, must-revalidate')

    def test_deliberate_failure_case(self):
        """This test is designed to always fail."""
        self.assertEqual(1, 2, "Deliberate failure: 1 is not equal to 2")

if __name__ == '__main__':
    unittest.main()


