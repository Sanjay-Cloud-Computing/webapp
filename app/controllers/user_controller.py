import boto3
import json
import logging
from flask import request, jsonify
from app.services.user_service import userService
from app.utilities.response_utils import response_handler
from app.utilities.metrics import record_api_call, record_api_duration
from time import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')

region = os.getenv('AWS_REGION') or 'us-east-1'

sns_client = boto3.client('sns', region_name=region)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_user():
    start_time = time()
    record_api_call('create_user')
    
    try:
        if not request.is_json:
            logger.warning("Invalid request: JSON expected")
            return response_handler(400)
        
        user_data = request.get_json()
        required_fields = {"first_name", "last_name", "password", "email", "token"}

        if not all(field in user_data for field in required_fields):
            logger.warning("Missing required fields in user data")
            return response_handler(400)

        if not set(user_data.keys()).issubset(required_fields):
            logger.warning("Unexpected fields in user data")
            return response_handler(400)

        # Pass validated data to the service layer
        result = userService.create_or_verify_user(user_data)

        # If user creation was successful, publish SNS message
        if result.get("sns_message"):
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=json.dumps(result["sns_message"]),
                Subject="User Registration - Email Verification"
            )
            logger.info("Published message to SNS for email verification")

        return jsonify(result["response"]), result["status_code"]

    except Exception as e:
        logger.exception("Unexpected error during create_user: %s", str(e))
        return response_handler(500)

    finally:
        record_api_duration('create_user', (time() - start_time) * 1000)
