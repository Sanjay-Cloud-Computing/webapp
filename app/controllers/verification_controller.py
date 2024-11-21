import logging
from flask import request, jsonify, abort
from datetime import datetime, timezone
from app.services.verification_service import VerificationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

verification_service = VerificationService()

def verify_email():
    try:
        # Extract parameters from the query string
        user_email = request.args.get('user')
        token = request.args.get('token')

        if not user_email or not token:
            logger.error("ERROR: Missing required parameters: user or token", extra={"severity": "ERROR"})
            abort(400, "Bad Request: Missing required parameters")

        logger.info(f"INFO: Processing verification for user: {user_email}", extra={"severity": "INFO"})
        
        # Call the service to verify the email
        result = verification_service.verify_email(user_email, token)

        if result:
            return jsonify({"message": "Email verified successfully"}), 200
        else:
            abort(400, "Verification failed or token expired")

    except Exception as e:
        logger.error(f"ERROR: Exception occurred during email verification: {e}", extra={"severity": "ERROR"})
        abort(400)
