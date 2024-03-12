from bcrypt import hashpw, gensalt, checkpw


def hash_salt_pw(pw: bytes) -> bytes:
    return hashpw(pw, gensalt())


def check_pw(pw: bytes, hashed_pw: bytes) -> bool:
    return checkpw(pw, hashed_pw)
