from app import db
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, DatabaseError
from app.utilities.response_utils import response_handler

def get_health():
    
    try:
        db.session.execute(text("SELECT 1")).fetchone()
        db.session.commit()
        return True

    except (OperationalError, DatabaseError):
        return False

