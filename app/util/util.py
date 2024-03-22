import base64
import datetime
import secrets
from hashlib import sha256

from bcrypt import hashpw, gensalt, checkpw


def simple_hash(pw: bytes) -> bytes:
    return sha256(pw).digest()


def simple_hash_str(pw: str) -> str:
    return simple_hash(pw.encode('utf-8')).hex()


def hash_salt_pw(pw: bytes) -> bytes:
    return hashpw(pw, gensalt())


def hash_salt_pw_str(pw: str) -> str:
    return hashpw(pw.encode('utf-8'), gensalt()).hex()


def check_pw(pw: bytes, hashed_pw: bytes) -> bool:
    return checkpw(pw, hashed_pw)


def generate_api_key():
    return secrets.token_urlsafe(32)


def now():
    return datetime.datetime.now(tz=datetime.timezone.utc)
