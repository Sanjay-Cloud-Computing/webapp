from  app.models.user_model import User
from datetime import datetime
from app import db
from app.utilities.login_user_utils import hash_password, is_valid_email
from app.utilities.utc_convert_datetime import format_datetime
from app.utilities.check_table_utils import check_and_create_users_table
from sqlalchemy import String, Integer, DateTime

class userService:
     
    def create_user(self, data):

            check_and_create_users_table()
            required_fields = ['email', 'first_name', 'last_name', 'password']
            
            if data == {}:
                 raise ValueError
            
            for field in required_fields:
               if field not in data or type(data[field]) is not str:
                    print("insss")
                    raise ValueError
               
            if not set(data.keys()).issubset(set(required_fields)):
                  raise ValueError
           
            empty_fields = [field for field in required_fields if field not in data or not data[field].strip()]
        
            if empty_fields:
                 raise ValueError
            
            if not is_valid_email(data['email']):
                 raise ValueError
        
            if User.query.filter_by(email=data['email']).first():
                 raise ValueError
        
            new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data['email'],
            email=data['email'],
            password=hash_password(data['password']),
            account_created=datetime.strptime(format_datetime(), "%Y-%m-%dT%H:%M:%S.%fZ"),
            account_updated=datetime.strptime(format_datetime(), "%Y-%m-%dT%H:%M:%S.%fZ")
            )
            db.session.add(new_user)
            db.session.commit() 
    
            return new_user
        