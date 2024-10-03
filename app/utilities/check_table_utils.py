from app.models.user_model import User
from app import db
from sqlalchemy import inspect

def check_and_create_users_table():
    inspector = inspect(db.engine)
    if User.__tablename__ not in inspector.get_table_names():
        db.create_all()
        return True
    else:
        return False
    