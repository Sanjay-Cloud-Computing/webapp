import logging
from app.models.user_model import User
from datetime import datetime, timezone, timedelta
from app import db
from app.utilities.login_user_utils import hash_password, is_valid_email
from app.utilities.utc_convert_datetime import format_datetime
from app.utilities.check_table_utils import check_and_create_users_table
from sqlalchemy import String, Integer, DateTime
import uuid
from app.models.verification_model import Verification
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class userService:
     
    def create_user(self, data):
        logger.info("INFO: Starting user creation process", extra={"severity": "INFO"})

        check_and_create_users_table()
        required_fields = ['email', 'first_name', 'last_name', 'password']
        
        if data == {}:
            logger.error("ERROR: Received empty data for user creation", extra={"severity": "ERROR"})
            raise ValueError
        
        for field in required_fields:
            if field not in data or type(data[field]) is not str:
                logger.error(f"ERROR: Missing or invalid field in data: {field}", extra={"severity": "ERROR"})
                raise ValueError
           
        if not set(data.keys()).issubset(set(required_fields)):
            logger.error("ERROR: Data contains unexpected fields", extra={"severity": "ERROR"})
            raise ValueError
       
        empty_fields = [field for field in required_fields if field not in data or not data[field].strip()]
    
        if empty_fields:
            logger.error(f"ERROR: Empty required fields: {empty_fields}", extra={"severity": "ERROR"})
            raise ValueError
        
        if not is_valid_email(data['email']):
            logger.error(f"ERROR: Invalid email format: {data['email']}", extra={"severity": "ERROR"})
            raise ValueError
    
        if User.query.filter_by(email=data['email']).first():
            logger.error(f"ERROR: User with email {data['email']} already exists", extra={"severity": "ERROR"})
            raise ValueError
    
        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data['email'],
            email=data['email'],
            password=hash_password(data['password']),
            account_created=datetime.strptime(format_datetime(), "%Y-%m-%dT%H:%M:%S.%fZ"),
            account_updated=datetime.strptime(format_datetime(), "%Y-%m-%dT%H:%M:%S.%fZ")
        )
        db.session.add(new_user)
        db.session.commit() 
        logger.info(f"INFO: User created successfully with ID {new_user.id}", extra={"severity": "INFO"})
        
        verification_token = str(uuid.uuid4())
        expiry = datetime.now(timezone.utc) + timedelta(minutes=2)

        verification_entry = Verification(
            user_id=new_user.id,
            verification_token=verification_token,
            expiry=expiry
        )

        db.session.add(verification_entry)
        db.session.commit()
        logger.info(f"INFO: Verification entry created for user ID {new_user.id} with token {verification_token}", extra={"severity": "INFO"})

        # Publish to SNS
        self.publish_to_sns(new_user.email, verification_token)
        return new_user

    def publish_to_sns(self, email, token):
        import boto3
        logger.info(f"INFO: Publishing verification token to SNS for email {email}", extra={"severity": "INFO"})
        
        sns = boto3.client('sns', region_name='us-east-1')
        topic_arn =  os.getenv('SNS_TOPIC_ARN')

        message = {
            'email': email,
            'verification_token': token
        }

        try:
            sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps(message),
                Subject='Verify Your Email'
            )
            logger.info(f"INFO: Successfully published message to SNS for email {email}", extra={"severity": "INFO"})
        except Exception as e:
            logger.error(f"ERROR: Failed to publish message to SNS for email {email}: {e}", extra={"severity": "ERROR"})
            raise
