import uuid
import enum

from sqlalchemy import func, Enum

# import app.util.util
from app.extensions import db


class Type(enum.Enum):
    setState = 0
    last_getState = 1
    getState_true = 2


class Usage(db.Model):
    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Uuid, db.ForeignKey('user.id'), nullable=False)
    actor_id = db.Column(db.Uuid, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(Enum(Type), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
