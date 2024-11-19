from app.models.user_model import User
from datetime import datetime, timezone
from app import db
from app.utilities.login_user_utils import hash_password, is_valid_email
from app.utilities.utc_convert_datetime import format_datetime
from app.utilities.check_table_utils import check_and_create_users_table
from sqlalchemy.exc import IntegrityError
from app.models.email_verification_model import EmailVerification
from app import db, bcrypt
from datetime import datetime, timezone, timedelta
from app.utilities.login_user_utils import is_valid_email
import uuid

class userService:

    def create_user(self, data):
        # Ensure the users table exists
        check_and_create_users_table()
        
        # Define required fields
        required_fields = ['email', 'first_name', 'last_name', 'password']
        
        # Validate request data
        if not data or not isinstance(data, dict):
            raise ValueError("Invalid data format")
        
        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in data or not data[field].strip()]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Validate email format
        email = data['email']
        if not is_valid_email(email):
            raise ValueError("Invalid email address")
        
        # Check for duplicate email
        if User.query.filter_by(email=email).first():
            raise ValueError("User with this email already exists")
        
        # Create a new user
        new_user = User(
            id=str(uuid.uuid4()),
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=email,
            email=email,
            password=hash_password(data['password']),
            account_created=datetime.now(timezone.utc),
            account_updated=datetime.now(timezone.utc),
            is_verified=False  # Initial status as unverified
        )
        
        try:
            # Save the new user to the database
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Database integrity error occurred while creating the user")

    def save_email_verification(self, user_id, token, expires_at):
        from app.models.email_verification_model import EmailVerification  # Ensure model is imported
        email_verification = EmailVerification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc)
        )
        
        try:
            # Save the email verification record to the database
            db.session.add(email_verification)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Database integrity error occurred while saving the email verification record")
