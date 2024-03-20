import datetime
import secrets
from hashlib import sha256

from bcrypt import hashpw, gensalt, checkpw


def simple_hash(pw: bytes) -> bytes:
    return sha256(pw).digest()


def hash_salt_pw(pw: bytes) -> bytes:
    return hashpw(pw, gensalt())


def check_pw(pw: bytes, hashed_pw: bytes) -> bool:
    return checkpw(pw, hashed_pw)


def generate_api_key():
    return secrets.token_urlsafe(32)


def now():
    return datetime.datetime.now(tz=datetime.timezone.utc)
