import uuid
from sqlalchemy import func, text, Enum, sql
from app.extensions import db
from app.models.users import Role


class State(db.Model):
    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    begin = db.Column(db.DateTime, nullable=True)
    end = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
