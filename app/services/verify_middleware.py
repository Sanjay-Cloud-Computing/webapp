import logging
from flask import abort
from app.models.verification_model import Verification
from app.models.user_model import User
from app import db
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_user_middleware(username):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info("INFO: Verifying user access with middleware", extra={"severity": "INFO"})
            
            try:
                logger.info(f"INFO: Verifying email from controller: {username}", extra={"severity": "INFO"})
                
                verification = db.session.query(Verification, User).join(User, Verification.user_id == User.id).filter(
                        User.email == username,
                        Verification.is_verified == True
                    ).first()
                
                print(verification)

                if not verification:
                    logger.warning(f"WARNING: Access denied for unverified user: {username}", extra={"severity": "WARNING"})
                    abort(403)  # Forbidden

                logger.info(f"INFO: User {username} is verified, proceeding to endpoint", extra={"severity": "INFO"})
                return func(*args, **kwargs)
            
            except Exception as e:
                logger.error(f"ERROR: Exception occurred in verify_user_middleware: {e}", extra={"severity": "ERROR"})
                abort(500)  # Internal Server Error
        
        return wrapper
    return decorator
