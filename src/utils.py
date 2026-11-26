import os

import bcrypt

def hash_password(password):
    """Hash a plaintext password using bcrypt, using a fresh random salt each time."""

    rounds = int(os.environ.get("BCRYPT_ROUNDS", 12))
    salt = bcrypt.gensalt(rounds=rounds)

    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(password, hashed):
    """Check a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def hash_user_passwords(users):
    """Return a copy of the users with each plaintext password replaced by its hash."""
    return [{**users, "password": hash_password(user["password"])} for user in users]