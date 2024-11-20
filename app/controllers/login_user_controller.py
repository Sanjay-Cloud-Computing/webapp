import logging
from flask import request, jsonify, abort, make_response
from .. import db
from flask_httpauth import HTTPBasicAuth
from app.models.user_model import User
from app.services.login_user_service import AuthService
from app.utilities.response_utils import response_handler
from app.utilities.utc_convert_datetime import format_datetime
from app.services.health_check_service import get_health
from app.utilities.check_table_utils import check_and_create_users_table
from app.utilities.utc_convert_datetime import change_date_str
from app.utilities.metrics import statsd_client, record_api_call, record_api_duration
from app.services.verify_middleware import verify_user_middleware
from time import time

auth = HTTPBasicAuth()
auth_service = AuthService()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@auth.verify_password
def verify_password(username, password):
    start_time = time()
    record_api_call('verify_password')  # Track API call
    logger.info("INFO: Verifying password", extra={"severity": "INFO"})
    
    try:
        if len(request.args) > 0:
            logger.error("ERROR: Invalid request parameters for verify_password", extra={"severity": "ERROR"})
            return abort(response_handler(400))
        if get_health():
            check_and_create_users_table()
            user = auth_service.verify_user_creds(username, password)
            if user:
                logger.info("INFO: User verified successfully", extra={"severity": "INFO"})
                return user
            else:
                logger.warning("ERROR: Unauthorized access attempt", extra={"severity": "ERROR"})
                abort(response_handler(401))
        else:
            logger.error("FATAL: Health check failed, aborting verification", extra={"severity": "FATAL"})
            abort(response_handler(503))
    finally:
        record_api_duration('verify_password', (time() - start_time) * 1000)  # Record total API call duration
        
@verify_user_middleware
def get_user_details():
    start_time = time()
    record_api_call('get_user_details')  # Track API call
    logger.info("INFO: Retrieving user details", extra={"severity": "INFO"})
    
    try:
        user_data = db.session.query(User).filter_by(email=auth.username()).first()
        logger.info(f"INFO: User data retrieved: {user_data}", extra={"severity": "INFO"})
        
        if not user_data.is_verified:
            abort(403)
        if request.data or len(request.args) > 0 or request.data.strip() == b'{}' or request.form:
            logger.error("ERROR: Invalid request data for get_user_details", extra={"severity": "ERROR"})
            return abort(response_handler(400))

        response_body = {
            "id": user_data.id,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "email": user_data.email, 
            "account_created": change_date_str(user_data.account_created),
            "account_updated": change_date_str(user_data.account_updated)
        }
        response = make_response(jsonify(response_body), 200) 
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Content-Type'] = 'application/json'
        logger.info("INFO: User details retrieved successfully", extra={"severity": "INFO"})
        return response
    finally:
        record_api_duration('get_user_details', (time() - start_time) * 1000)  # Record total API call duration

def update_user_details():
    start_time = time()
    record_api_call('update_user_details')  # Track API call
    logger.info("INFO: Updating user details", extra={"severity": "INFO"})
    
    try:
        if not request.data or request.data is None or len(request.args) > 0 or request.data.strip() == b'{}':
            logger.error("ERROR: Missing or invalid request data", extra={"severity": "ERROR"})
            return response_handler(400)
        if not request.content_type or request.content_type != 'application/json':
            logger.error("ERROR: Invalid content type", extra={"severity": "ERROR"})
            return response_handler(400)
        if not request.data or request.data.strip() == b'':
            logger.error("ERROR: Empty request data", extra={"severity": "ERROR"})
            return response_handler(400)
        
        data = request.get_json()
        user_data = db.session.query(User).filter_by(email=auth.username()).first()
        allowed_fields = {"first_name", "last_name", "password"}

        if not set(data.keys()).issubset(allowed_fields):
            logger.error("ERROR: Unallowed fields in request data", extra={"severity": "ERROR"})
            return response_handler(400)

        auth_service.update_user(user_data.id, data)
        logger.info("INFO: User details updated successfully", extra={"severity": "INFO"})
        return response_handler(204)
    
    except ValueError as ve:
        logger.error(f"ERROR: Value error during update: {ve}", extra={"severity": "ERROR"})
        return response_handler(400)
    
    except Exception as e:
        logger.exception("FATAL: Exception during update_user_details", extra={"severity": "FATAL"})
        return response_handler(400)
    finally:
        record_api_duration('update_user_details', (time() - start_time) * 1000)  # Record total API call duration
