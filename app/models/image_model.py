from datetime import datetime, timezone
from app import db
import uuid

class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<Image {self.file_name}>"
