import logging
from flask import request, jsonify, make_response
from app import db
from app.models.user_model import User
from app.models.image_model import Image
from app.services.image_service import upload_image_to_s3, delete_image_from_s3
from app.utilities.response_utils import response_handler
from app.controllers.login_user_controller import auth
from app.utilities.metrics import statsd_client, record_api_call, record_api_duration
from time import time
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
S3_BUCKET = os.getenv('S3_BUCKET_NAME')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@auth.login_required
def upload_profile_picture():
    start_time = time()
    record_api_call('upload_profile_picture')  # Record API call
    user = auth.current_user()
    logger.info("INFO: User authenticated for upload_profile_picture", extra={"severity": "INFO"})
    
    file = request.files.get('profilePic')
    if not file:
        statsd_client.incr('upload_profile_picture.error')  # Track error count
        logger.error("ERROR: No file provided for upload", extra={"severity": "ERROR"})
        return response_handler(400)
    
    existing_image = Image.query.filter_by(user_id=user.id).first()
    
    try:
        # Track S3 upload duration
        s3_start_time = time()
        s3_url = upload_image_to_s3(file, user.id)
        statsd_client.timing('upload_profile_picture.s3_upload_time', (time() - s3_start_time) * 1000)
        logger.info("INFO: Image uploaded to S3 successfully", extra={"severity": "INFO"})

        if existing_image:
            delete_image_from_s3(existing_image.url)
            existing_image.file_name = file.filename
            existing_image.url = s3_url
            existing_image.upload_date = datetime.now(timezone.utc)
        else:
            new_image = Image(file_name=file.filename, url=s3_url, user_id=user.id)
            db.session.add(new_image)
        
        db.session.commit()
        
        # Track API processing time
        statsd_client.timing('upload_profile_picture.api_processing_time', (time() - start_time) * 1000)
        logger.info("INFO: Image upload and database update successful", extra={"severity": "INFO"})

        response_body = {
            "file_name": file.filename,
            "id": existing_image.id if existing_image else new_image.id,
            "url": s3_url,
            "upload_date": new_image.upload_date,
            "user_id": user.id
        }
        return make_response(jsonify(response_body), 201)
    
    except Exception as e:
        statsd_client.incr('upload_profile_picture.error')  # Track error count on exception
        logger.exception("FATAL: Exception during upload_profile_picture", extra={"severity": "FATAL"})
        return response_handler(400)
    finally:
        record_api_duration('upload_profile_picture', (time() - start_time) * 1000)  # Record total API call duration

@auth.login_required
def get_profile_picture():
    start_time = time()
    record_api_call('get_profile_picture')  # Record API call
    user = auth.current_user()
    image = Image.query.filter_by(user_id=user.id).first()
    
    if not image:
        logger.warning("ERROR: No profile picture found for user", extra={"severity": "ERROR"})
        return response_handler(404)

    response_body = {
        "file_name": image.file_name,
        "id": image.id,
        "url": image.url,
        "upload_date": image.upload_date,
        "user_id": image.user_id
    }
    record_api_duration('get_profile_picture', (time() - start_time) * 1000)  # Record total API call duration
    logger.info("INFO: Profile picture retrieved successfully", extra={"severity": "INFO"})
    return make_response(jsonify(response_body), 200)

@auth.login_required
def delete_profile_picture():
    start_time = time()
    record_api_call('delete_profile_picture')  # Record API call
    user = auth.current_user()
    image = Image.query.filter_by(user_id=user.id).first()
    
    if not image:
        logger.warning("ERROR: No profile picture found to delete", extra={"severity": "ERROR"})
        return response_handler(404)
    
    try:
        # Extract the S3 key from the URL
        s3_key = image.url.split(f"{S3_BUCKET}/")[-1]
        delete_image_from_s3(s3_key)
        db.session.delete(image)
        db.session.commit()
        logger.info("INFO: Profile picture deleted successfully", extra={"severity": "INFO"})
        return response_handler(204)
    
    except Exception as e:
        logger.exception("FATAL: Exception during delete_profile_picture", extra={"severity": "FATAL"})
        return response_handler(400)
    finally:
        record_api_duration('delete_profile_picture', (time() - start_time) * 1000)  # Record total API call duration
