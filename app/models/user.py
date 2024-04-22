import enum
import uuid
from sqlalchemy import text, Enum

import app.util.util
from app.extensions import db


class Role(enum.Enum):
    deactivated = 0
    admin = 1
    actor = 2
    user = 3
    guest = 4
    maintenance = 5

    def __str__(self):
        return self.name


class User(db.Model):
    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False, unique=True)
    role = db.Column(Enum(Role), nullable=False, server_default=text(Role.guest.name))
    email = db.Column(db.String, nullable=True, unique=True)
    password = db.Column(db.String, nullable=True)
    signal_id = db.Column(db.String, nullable=True, unique=True)
    signal_phone_nr = db.Column(db.String, nullable=True, unique=True)
    api_key = db.Column(db.String(128), nullable=True, unique=True, default=None)
    updated_at = db.Column(db.DateTime, nullable=False, default=app.util.util.now())
    created_at = db.Column(db.DateTime, nullable=False, default=app.util.util.now())
