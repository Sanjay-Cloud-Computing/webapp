import logging
from flask import request, abort, make_response, jsonify
from datetime import datetime
from app.services.user_service import userService
from app.utilities.response_utils import response_handler
from app.services.health_check_service import get_health
from app.utilities.utc_convert_datetime import format_datetime, change_date_str
from app.services.email_service import send_email
from app.utilities.metrics import statsd_client, record_api_call, record_api_duration
from time import time

user_service = userService()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_user():
    start_time = time()
    record_api_call('create_user')
    
    # Track API call
    logger.info("INFO: Attempting to create new user", extra={"severity": "INFO"})
    
    try:
        data = request.get_json()
        
        if data is None or len(request.args) > 0:
            logger.error("ERROR: Invalid request data for create_user", extra={"severity": "ERROR"})
            return response_handler(400)
        
        health_check = get_health()
        
        if health_check:
            new_user = user_service.create_user(data)
            
            # Send a welcome email
            send_email(new_user.email, "Welcome!", "Thanks for signing up")
            logger.info("INFO: Welcome email sent", extra={"severity": "INFO"})
            
            response_body = {
                "id": new_user.id,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email,
                "account_created": change_date_str(new_user.account_created),
                "account_updated": change_date_str(new_user.account_updated)
            }
            
            response = make_response(jsonify(response_body), 201)
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Content-Type'] = 'application/json'
            
            logger.info("INFO: User created successfully", extra={"severity": "INFO"})
            return response
        else:
            logger.error("FATAL: Health check failed, aborting user creation", extra={"severity": "FATAL"})
            return abort(response_handler(503))
    
    except ValueError as ve:
        logger.error(f"ERROR: Value error during user creation: {ve}", extra={"severity": "ERROR"})
        return response_handler(400)
    
    except Exception as e:
        logger.exception("FATAL: Exception during create_user", extra={"severity": "FATAL"})
        return response_handler(400)
    
    finally:
        # Record total API call duration
        record_api_duration('create_user', (time() - start_time) * 1000)
