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
from app.models.email_verification_model import EmailVerification
import os
from dotenv import load_dotenv

user_service = userService()
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')
sns_client = boto3.client('sns', region_name=os.getenv('AWS_REGION') or 'us-east-1')

def create_user():
    start_time = time()
    record_api_call('create_user')  # Track API call
    logger.info("INFO: Attempting to create new user", extra={"severity": "INFO"})
    
    try:
        data = request.get_json()
        
        if data is None or len(request.args) > 0:
            logger.error("ERROR: Invalid request data for create_user", extra={"severity": "ERROR"})
            return response_handler(400)
        
        health_check = get_health()
        
        if health_check:
            new_user = user_service.create_user(data)
            
            # Generate verification token and expiration time
            verification_token = str(uuid.uuid4())
            expiration_time = datetime.now(datetime.timezone.utc) + timedelta(minutes=2)

            # Save verification token to database
            email_verification = EmailVerification(
                id=str(uuid.uuid4()),
                user_id=new_user.id,
                email=new_user.email,
                token=verification_token,
                created_at=datetime.now(datetime.timezone.utc),
                expires_at=expiration_time
            )
            db.session.add(email_verification)
            db.session.commit()
            
            # Publish message to SNS
            sns_message = {
                "user_id": new_user.id,
                "email": new_user.email,
                "first_name": new_user.first_name,
                "verification_token": verification_token,
                "expires_at": expiration_time.isoformat()
            }
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=json.dumps(sns_message),
                Subject="User Registration - Email Verification"
            )
            logger.info("INFO: Published message to SNS for user ID: %s", new_user.id)
            
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
        record_api_duration('create_user', (time() - start_time) * 1000)