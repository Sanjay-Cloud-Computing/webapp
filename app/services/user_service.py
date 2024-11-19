from app.models.user_model import User
from app.models.email_verification_model import EmailVerification
from app import db, bcrypt
from datetime import datetime, timezone, timedelta
from app.utilities.login_user_utils import is_valid_email
import uuid

class userService:

    @staticmethod
    def create_or_verify_user(data):
        # Extract fields from data
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        password = data.get("password")
        email = data.get("email")

        # Validate email format
        if not is_valid_email(email):
            raise ValueError("Invalid email")

        existing_user = User.query.filter_by(email=email).first()

        # Verify token if user exists
        if existing_user:
            verification_record = EmailVerification.query.filter_by(user_id=existing_user.id, token=token).first()
            if not verification_record or verification_record.expires_at < datetime.now(timezone.utc):
                raise ValueError("Invalid or expired token")

            # Update user verification status
            existing_user.is_verified = True
            existing_user.account_updated = datetime.now(timezone.utc)
            db.session.commit()
            return {
                "response": {"message": "Email verified successfully"},
                "status_code": 200
            }

        # Create new user
        new_user = User(
            id=str(uuid.uuid4()),
            first_name=first_name,
            last_name=last_name,
            password=bcrypt.generate_password_hash(password).decode('utf-8'),
            email=email,
            account_created=datetime.now(timezone.utc),
            account_updated=datetime.now(timezone.utc),
            is_verified=False
        )
        db.session.add(new_user)
        db.session.commit()

        # Generate verification token
        verification_token = str(uuid.uuid4())
        expiration_time = datetime.now(timezone.utc) + timedelta(minutes=2)

        # Save token in database
        email_verification = EmailVerification(
            id=str(uuid.uuid4()),
            user_id=new_user.id,
            email=new_user.email,
            token=verification_token,
            created_at=datetime.now(timezone.utc),
            expires_at=expiration_time
        )
        db.session.add(email_verification)
        db.session.commit()

        # Prepare SNS message
        sns_message = {
            "user_id": new_user.id,
            "email": new_user.email,
            "first_name": new_user.first_name,
            "verification_token": verification_token,
            "expires_at": expiration_time.isoformat()
        }

        return {
            "response": {
                "id": new_user.id,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email,
                "account_created": new_user.account_created,
                "account_updated": new_user.account_updated
            },
            "status_code": 201,
            "sns_message": sns_message
        }
