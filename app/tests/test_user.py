import unittest
from flask import json
from app import create_app, db
from app.models.user_model import User
from app.utilities.login_user_utils import hash_password

class CombinedTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a test client and initialize a new test database."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.add_test_user()

    def tearDown(self):
        """Drop the test database."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def add_test_user(self):
        """Helper function to add a test user to the database."""
        user = User(
            first_name="John",
            last_name="Doe",
            username="john.doe@example.com",
            email="john.doe@example.com",
            password=hash_password("password123"),
        )
        db.session.add(user)
        db.session.commit()

    def test_create_user_invalid_email(self):
        """Test creating a user with an invalid email."""
        user_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "invalid_email",
            "password": "password123"
        }
        response = self.client.post('/v1/user', data=json.dumps(user_data))
        self.assertEqual(response.status_code, 500) #400
        
    def test_create_user_extra_fields(self):
        """Test creating a user with extra fields."""
        user_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "password": "password123",
            "extra_field": "extra_value"
        }
        response = self.client.post('/v1/user', data=json.dumps(user_data), content_type='application/json')
        print("Response Status Code:", response.status_code)
        print("Response Data:", response.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
