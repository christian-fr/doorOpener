import uuid

from sqlalchemy import func

# import app.util.util
from app.extensions import db


class Usage(db.Model):
    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    actor_id = db.Column(db.Uuid, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
