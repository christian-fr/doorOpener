import enum
import uuid
from sqlalchemy import func, text, Enum
from app.extensions import db


class Mode(enum.Enum):
    unset = 0
    read = 1
    write = 2

    def __str__(self):
        return self.name


class Scope(db.Model):
    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Uuid, db.ForeignKey('user.id'), nullable=False)
    actor_id = db.Column(db.Uuid, db.ForeignKey('user.id'), nullable=False)
    mode = db.Column(Enum(Mode), nullable=False, server_default=text(Mode.unset.name))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
