import hashlib


def encode_password(password):
    return hashlib.md5(password.encode()).hexdigest()

