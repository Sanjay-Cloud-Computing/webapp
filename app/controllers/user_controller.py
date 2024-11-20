import boto3
import json
from flask import request, abort, make_response, jsonify
from app.services.user_service import userService
from app.utilities.response_utils import response_handler
from app.utilities.metrics import statsd_client, record_api_call, record_api_duration
from time import time
import os
from dotenv import load_dotenv

load_dotenv()

user_service = userService()
sns_client = boto3.client('sns')

SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')
print(SNS_TOPIC_ARN)

def create_user():
    start_time = time()
    record_api_call('create_user')
    
    try:
        data = request.get_json()
        if data is None or len(request.args) > 0:
            return response_handler(400)
        
        new_user, verification_token = user_service.create_user(data)
        
        # Publish message to SNS topic
        sns_payload = {
            "user_id": new_user.id,
            "email": new_user.email,
            "verification_token": verification_token
        }
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(sns_payload),
            Subject="New User Account Verification"
        )
        
        response_body = {
            "id": new_user.id,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "account_created": new_user.account_created.isoformat(),
            "account_updated": new_user.account_updated.isoformat()
        }
        
        response = make_response(jsonify(response_body), 201)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Content-Type'] = 'application/json'
        return response
    
    except Exception as e:
        return response_handler(400)
    finally:
        record_api_duration('create_user', (time() - start_time) * 1000)

def block_unverified_users():
    def wrapper(func):
        def inner(*args, **kwargs):
            user_id = request.headers.get('User-ID')  # Assuming user ID is sent in the request header
            if not user_service.is_user_verified(user_id):
                return response_handler(403, message="User account not verified")
            return func(*args, **kwargs)
        return inner
    return wrapper
