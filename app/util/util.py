import datetime
import secrets
from functools import cache
from hashlib import sha256

from bcrypt import hashpw, gensalt, checkpw


def simple_hash(pw: bytes) -> bytes:
    return sha256(pw).digest()


def simple_hash_str(pw: str) -> str:
    return simple_hash(pw.encode('utf-8')).hex()


def hash_salt_pw(pw: bytes) -> bytes:
    return hashpw(pw, gensalt())


@cache
def hash_salt_pw_str(pw: str) -> str:
    return hashpw(pw.encode('utf-8'), gensalt()).decode('utf-8')


def check_pw(pw: bytes, hashed_pw: bytes) -> bool:
    return checkpw(pw, hashed_pw)


@cache
def check_pw_str(pw: str, hashed_pw: str) -> bool:
    return checkpw(pw.encode('utf-8'), hashed_pw.encode('utf-8'))


def generate_api_key():
    return secrets.token_hex(32)


def now():
    return datetime.datetime.now(tz=datetime.timezone.utc)
