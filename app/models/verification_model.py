from app import db
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from datetime import datetime, timedelta, timezone

class Verification(db.Model):
    __tablename__ = 'verification'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    verification_token = Column(String(255), nullable=False, unique=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    expiry = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)+ timedelta(minutes=2))
