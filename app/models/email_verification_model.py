from datetime import datetime, timezone
from app import db
import uuid

class EmailVerification(db.Model):
    __tablename__ = 'email_verifications'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
