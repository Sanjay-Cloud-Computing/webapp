from datetime import datetime, timezone, timedelta
from app import db
import uuid

class Verification(db.Model):
    __tablename__ = 'verification'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    verification_token = db.Column(db.String(255), nullable=False, unique=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    expiry = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc) + timedelta(minutes=2))
