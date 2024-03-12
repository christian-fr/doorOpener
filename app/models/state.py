import uuid
from sqlalchemy import func, text, Enum, sql
from app.extensions import db
from app.models.users import Role


class State(db.Model):
    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    api_key = db.Column(db.String(128), nullable=True, unique=True, default=None)
    is_active = db.Column(db.Boolean, server_default=sql.true())
    role = db.Column(Enum(Role), nullable=False, server_default=text(Role.guest.name))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
