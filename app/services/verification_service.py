import logging
from datetime import datetime, timezone
from app import db
from app.models.verification_model import Verification
from app.models.user_model import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VerificationService:
    def verify_email(self, user_email, token):
        try:
            # Fetch verification record
            verification = db.session.query(Verification).join(User).filter(
                User.email == user_email,
                Verification.verification_token == token
            ).first()

            if not verification:
                logger.warning(f"WARNING: No verification record found for user: {user_email} and token: {token}", extra={"severity": "WARNING"})
                return False

            # Check if the token is expired
            if verification.expiry < datetime.now(timezone.utc):
                logger.warning(f"WARNING: Token expired for user: {user_email}", extra={"severity": "WARNING"})
                return False

            # Update verification status
            verification.is_verified = True
            db.session.commit()

            logger.info(f"INFO: Successfully verified user {user_email}", extra={"severity": "INFO"})
            return True

        except Exception as e:
            logger.error(f"ERROR: Exception in verify_email service: {e}", extra={"severity": "ERROR"})
            raise
