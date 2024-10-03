from app.models.user_model import User
from app import db
from app.utilities.login_user_utils import verify_password, hash_password

class AuthService:
    
    @staticmethod
    def verify_user_creds(username, password):
        user = User.query.filter_by(username=username).first()
        if user and verify_password(user.password, password):
            return user
        return None
    
    def update_user(self, user_id, data):
        user_data = User.query.get(user_id)
        
        if not user_data:
            raise ValueError
        
        if "first_name" in data:
            if not data['first_name'].strip():
                raise ValueError
            user_data.first_name = data['first_name']

        if "last_name" in data:
            if not data['last_name'].strip():
                raise ValueError
            user_data.last_name = data['last_name']

        if "password" in data:
            if not data['password'].strip():
                raise ValueError
            user_data.password = hash_password(data['password'])

        db.session.commit()

        return user_data
