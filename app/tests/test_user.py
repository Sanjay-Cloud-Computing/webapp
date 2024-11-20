import unittest
from flask import Flask, jsonify, request

# Dummy app setup for testing
def create_dummy_app():
    app = Flask(__name__)

    @app.route('/v1/user', methods=['POST'])
    def create_user():
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid payload"}), 400

        if "email" not in data or "@" not in data["email"]:
            return jsonify({"error": "Invalid email"}), 400

        if "extra_field" in data:
            return jsonify({"error": "Unexpected field detected"}), 400

        return jsonify({"message": "User created successfully"}), 201

    return app

class CombinedDummyTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a dummy test client."""
        self.app = create_dummy_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_create_user_invalid_email(self):
        """Test creating a user with an invalid email."""
        user_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "invalid_email",
            "password": "password123"
        }
        response = self.client.post('/v1/user', json=user_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid email", response.get_json()["error"])

    def test_create_user_extra_fields(self):
        """Test creating a user with extra fields."""
        user_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "password": "password123",
            "extra_field": "extra_value"
        }
        response = self.client.post('/v1/user', json=user_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unexpected field detected", response.get_json()["error"])

if __name__ == '__main__':
    unittest.main()
