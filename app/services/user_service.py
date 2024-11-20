from app.models.user_model import User
from app.models.user_verification import UserVerification
from app import db
from app.utilities.login_user_utils import hash_password, is_valid_email
from datetime import datetime
import uuid

class userService:
    def create_user(self, data):
        required_fields = ['email', 'first_name', 'last_name', 'password']
        for field in required_fields:
            if field not in data or not data[field].strip():
                raise ValueError("Missing required field")

        if not is_valid_email(data['email']):
            raise ValueError("Invalid email format")

        if User.query.filter_by(email=data['email']).first():
            raise ValueError("Email already exists")
        
        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data['email'],
            email=data['email'],
            password=hash_password(data['password']),
            account_created=datetime.now(),
            account_updated=datetime.now()
        )
        db.session.add(new_user)
        db.session.flush()  # Flush to get the new user's ID

        # Create verification token
        verification_token = str(uuid.uuid4())
        user_verification = UserVerification(
            user_id=new_user.id,
            verification_token=verification_token
        )
        db.session.add(user_verification)
        db.session.commit()
        
        return new_user, verification_token

    def is_user_verified(self, user_id):
        user_verification = UserVerification.query.filter_by(user_id=user_id).first()
        return user_verification.verified if user_verification else False
