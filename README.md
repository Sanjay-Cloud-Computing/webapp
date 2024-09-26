# Health Check App using Flask

This Flask app exposes a health check endpoint (`/healthz`) to verify the status of the application and its connection to a MySQL database. The application uses SQLAlchemy for database interactions and leverages `python-dotenv` for managing environment variables.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Endpoints](#endpoints)
- [Error Handling](#error-handling)

## Requirements

Ensure you have the following installed on your machine:

- Python 3.6 or higher
- MySQL database
- Flask
- SQLAlchemy
- `python-dotenv` for environment variable management

## Installation

1. ### Clone the Repository

        git clone <https://github.com/Sanjay-Cloud-Computing/webapp.git>
        cd repo webapp

2. ### Create and Activate a Virtual Environment

        pip3 install virtualenv
        virtualenv env
        source env/bin/activate

3. ### Install Dependencies: Install the required Python packages by running

        pip install -r src/requirements.txt

## Set Up Environment Variables

Create a .env file in the root of the project to store your MySQL credentials and other environment variables.

### Structural format of .env file as below

    DB_USERNAME=your_db_username
    DB_PASSWORD=your_db_password
    DB_NAME=your_db_name
    DB_HOST=localhost
    DB_PORT=3306

    These values will be loaded automatically by python-dotenv

## Running the Application

1. Make sure your MySQL database is up and running
2. Run the Flask application: python3 src/app.py
3. Visit the /healthz endpoint in your browser

## Endpoints

**/healthz**
    This endpoint checks the health of the application and the connection to the MySQL database.

    Method: GET

    Response:
        200 OK: The application is healthy, and the database connection is working.
        503 Service Unavailable: The application or the database connection is not working.

## Error Handling

1. 400 Bad Request: Returned if the request contains query parameters or form data, which are not allowed.
2. 503 Service Unavailable: Returned if there is a problem connecting to the database.
3. 405 Method Not Allowed: Returned if a request is made to /healthz with any method other than GET.
4. 404 Not Found: Returned if a non-existent route is accessed.

All responses are returned without any payload and include the Cache-Control: no-cache header to prevent caching
