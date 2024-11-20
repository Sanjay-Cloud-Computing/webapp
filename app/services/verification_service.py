import datetime
from app import db
from app.models.user_model import User

def verify_email(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise ValueError("Invalid user ID")
    
    if user.is_verified:
        raise ValueError("User is already verified")
    
    user.is_verified = True
    user.account_updated = datetime.datetime.now(datetime.timezone.utc)
    db.session.commit()
