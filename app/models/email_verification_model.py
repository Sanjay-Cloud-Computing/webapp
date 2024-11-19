from app import db
from datetime import datetime, timezone
import uuid

class EmailVerification(db.Model):
    __tablename__ = 'email_verifications'

    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<EmailVerification {self.email}>"
