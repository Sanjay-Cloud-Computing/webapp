import logging
from flask import abort
from app.models.verification_model import Verification

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_user_middleware(func):
    def wrapper(*args, **kwargs):
        logger.info("INFO: Verifying user access with middleware", extra={"severity": "INFO"})
        
        try:
            user_email = auth.username()
            logger.info(f"INFO: Retrieved user email from authentication: {user_email}", extra={"severity": "INFO"})
            
            verification = db.session.query(Verification).join(User).filter(
                User.email == user_email,
                Verification.is_verified == True
            ).first()

            if not verification:
                logger.warning(f"WARNING: Access denied for unverified user: {user_email}", extra={"severity": "WARNING"})
                abort(403)  # Forbidden

            logger.info(f"INFO: User {user_email} is verified, proceeding to endpoint", extra={"severity": "INFO"})
            return func(*args, **kwargs)
        
        except Exception as e:
            logger.error(f"ERROR: Exception occurred in verify_user_middleware: {e}", extra={"severity": "ERROR"})
            abort(500)  # Internal Server Error
    
    return wrapper
