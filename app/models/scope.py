import uuid
from sqlalchemy import func, text, Enum, sql
from app.extensions import db


class Scope(db.Model):
    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    actor_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
